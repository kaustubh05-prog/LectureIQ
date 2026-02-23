import logging
import os
import tempfile
import uuid
from datetime import datetime

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.flashcard import Flashcard
from app.models.lecture import Lecture, ProcessingStatus
from app.models.mcq import MCQ
from app.models.note import Note
from app.models.resource import Resource
from app.models.transcript import Transcript
from app.services.generator import (
    extract_key_concepts,
    generate_flashcards,
    generate_mcqs,
    generate_notes,
)
from app.services.resource_linker import get_resources_for_topics
from app.services.storage import storage_service
from app.services.transcriber import transcribe_audio
from app.config import settings

logger = logging.getLogger(__name__)


def _set_progress(db, lecture: Lecture, status: ProcessingStatus, progress: int, error: str = None):
    lecture.status = status
    lecture.progress = progress
    if error:
        lecture.error_message = error[:500]
    if status == ProcessingStatus.COMPLETED:
        lecture.processed_at = datetime.utcnow()
    db.commit()


@celery_app.task(
    bind=True,
    max_retries=3,
    name="app.tasks.process_lecture.run",
)
def process_lecture_task(self, lecture_id: str):
    """
    Full processing pipeline:
      5%  → Start
      10% → Audio retrieved
      40% → Transcription done
      50% → Concepts extracted
      65% → Notes generated
      75% → Flashcards generated
      85% → MCQs generated
      95% → Resources found
     100% → Completed ✅
    """
    db = SessionLocal()
    tmp_audio_path = None

    try:
        lecture = db.query(Lecture).filter(Lecture.id == lecture_id).first()
        if not lecture:
            logger.error("Lecture %s not found — aborting task", lecture_id)
            return

        logger.info("[%s] ▶ Pipeline started", lecture_id)
        _set_progress(db, lecture, ProcessingStatus.PROCESSING, 5)

        # ── Step 1: Get audio ──────────────────────────────────────────
        logger.info("[%s] Fetching audio...", lecture_id)
        tmp_audio_path = storage_service.get_local_path(lecture.s3_key)
        _set_progress(db, lecture, ProcessingStatus.PROCESSING, 10)

        # ── Step 2: Transcribe ─────────────────────────────────────────
        logger.info("[%s] Transcribing...", lecture_id)
        result = transcribe_audio(tmp_audio_path, model_name=settings.whisper_model)

        db.add(Transcript(
            id=str(uuid.uuid4()),
            lecture_id=lecture_id,
            full_text=result["full_text"],
            segments=result["segments"],
            language=result.get("language", "unknown"),
        ))

        # Set duration from last segment
        if result["segments"]:
            lecture.duration = int(result["segments"][-1].get("end", 0))

        db.commit()
        _set_progress(db, lecture, ProcessingStatus.PROCESSING, 40)
        logger.info("[%s] Transcription done — %d segments", lecture_id, len(result["segments"]))

        full_text = result["full_text"]

        # ── Step 3: Extract concepts ───────────────────────────────────
        logger.info("[%s] Extracting key concepts...", lecture_id)
        concepts = extract_key_concepts(full_text)
        logger.info("[%s] Concepts: %s", lecture_id, concepts)
        _set_progress(db, lecture, ProcessingStatus.PROCESSING, 50)

        # ── Step 4: Notes ──────────────────────────────────────────────
        logger.info("[%s] Generating notes...", lecture_id)
        notes_md = generate_notes(full_text)
        db.add(Note(
            id=str(uuid.uuid4()),
            lecture_id=lecture_id,
            content=notes_md,
            key_concepts=concepts,
        ))
        db.commit()
        _set_progress(db, lecture, ProcessingStatus.PROCESSING, 65)

        # ── Step 5: Flashcards ─────────────────────────────────────────
        logger.info("[%s] Generating flashcards...", lecture_id)
        for i, fc in enumerate(generate_flashcards(full_text)):
            db.add(Flashcard(
                id=str(uuid.uuid4()),
                lecture_id=lecture_id,
                question=fc["question"],
                answer=fc["answer"],
                order=i,
            ))
        db.commit()
        _set_progress(db, lecture, ProcessingStatus.PROCESSING, 75)

        # ── Step 6: MCQs ───────────────────────────────────────────────
        logger.info("[%s] Generating MCQs...", lecture_id)
        for i, mcq in enumerate(generate_mcqs(full_text)):
            db.add(MCQ(
                id=str(uuid.uuid4()),
                lecture_id=lecture_id,
                question=mcq["question"],
                options=mcq["options"],
                correct_index=mcq["correct_index"],
                explanation=mcq["explanation"],
                order=i,
            ))
        db.commit()
        _set_progress(db, lecture, ProcessingStatus.PROCESSING, 85)

        # ── Step 7: Resources (non-critical) ───────────────────────────
        logger.info("[%s] Finding resources...", lecture_id)
        try:
            for res in get_resources_for_topics(concepts):
                db.add(Resource(
                    id=str(uuid.uuid4()),
                    lecture_id=lecture_id,
                    type=res["type"],
                    title=res["title"],
                    url=res["url"],
                    thumbnail_url=res.get("thumbnail_url"),
                    topic=res.get("topic"),
                    relevance_score=res.get("relevance_score", 1.0),
                ))
            db.commit()
        except Exception as e:
            # Resource failure must NEVER fail the whole pipeline
            logger.warning("[%s] Resource linking failed (non-fatal): %s", lecture_id, e)

        _set_progress(db, lecture, ProcessingStatus.PROCESSING, 95)

        # ── Done ───────────────────────────────────────────────────────
        _set_progress(db, lecture, ProcessingStatus.COMPLETED, 100)
        logger.info("[%s] ✅ Pipeline complete!", lecture_id)

    except Exception as exc:
        logger.error("[%s] Pipeline failed: %s", lecture_id, exc, exc_info=True)

        retries_left = self.max_retries - self.request.retries
        if retries_left > 0:
            logger.info("[%s] Retrying... (%d attempts left)", lecture_id, retries_left)
            raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
        else:
            # All retries exhausted — mark as FAILED
            try:
                lec = db.query(Lecture).filter(Lecture.id == lecture_id).first()
                if lec:
                    _set_progress(db, lec, ProcessingStatus.FAILED, 0, error=str(exc))
            except Exception:
                pass
            raise

    finally:
        db.close()
        # Clean up S3-downloaded temp files
        if (
            tmp_audio_path and
            os.path.exists(tmp_audio_path) and
            tmp_audio_path.startswith(tempfile.gettempdir())
        ):
            try:
                os.unlink(tmp_audio_path)
                logger.debug("Cleaned up temp file: %s", tmp_audio_path)
            except Exception:
                pass
