import logging
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.lecture import Lecture, ProcessingStatus
from app.models.user import User
from app.schemas.lecture import (
    FlashcardResponse,
    LectureDetailResponse,
    LectureResponse,
    LectureStatusResponse,
    MCQResponse,
    ResourceResponse,
    TranscriptData,
)
from app.services.storage import storage_service
from app.tasks.process_lecture import process_lecture_task
from app.utils.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {"mp3", "wav", "m4a", "ogg", "flac"}
MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024  # 100 MB


@router.post("/upload", response_model=LectureResponse, status_code=status.HTTP_201_CREATED)
async def upload_lecture(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ── Validate file type ──────────────────────────────────────────────
    filename = file.filename or "upload"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '.{ext}' not supported. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    # ── Read + validate size ────────────────────────────────────────────
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large. Maximum allowed size is 100 MB.",
        )

    # ── Store audio ─────────────────────────────────────────────────────
    lecture_id = str(uuid.uuid4())
    try:
        storage_key = storage_service.save_audio(file_bytes, lecture_id, ext)
    except Exception as e:
        logger.error("Audio storage failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store the audio file. Please try again.",
        )

    # ── Create DB record ────────────────────────────────────────────────
    lecture_title = (title or filename.rsplit(".", 1)[0]).strip()[:200] or "Untitled Lecture"
    lecture = Lecture(
        id=lecture_id,
        user_id=current_user.id,
        title=lecture_title,
        s3_key=storage_key,
        status=ProcessingStatus.UPLOADING,
        progress=0,
    )
    db.add(lecture)
    db.commit()
    db.refresh(lecture)

    # ── Queue Celery task ───────────────────────────────────────────────
    process_lecture_task.delay(lecture_id)
    logger.info(
        "Lecture %s uploaded by user %s → %s backend",
        lecture_id, current_user.id, storage_service.get_backend()
    )

    return lecture


@router.get("", response_model=List[LectureResponse])
def list_lectures(
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lectures = (
        db.query(Lecture)
        .filter(Lecture.user_id == current_user.id)
        .order_by(Lecture.uploaded_at.desc())
        .offset((page - 1) * limit)
        .limit(min(limit, 50))
        .all()
    )
    return lectures


@router.get("/{lecture_id}/status", response_model=LectureStatusResponse)
def get_status(
    lecture_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lecture = _get_lecture_or_404(db, lecture_id, current_user.id)
    return LectureStatusResponse(
        id=lecture.id,
        status=lecture.status.value,
        progress=lecture.progress,
        error_message=lecture.error_message,
    )


@router.get("/{lecture_id}", response_model=LectureDetailResponse)
def get_lecture(
    lecture_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lecture = _get_lecture_or_404(db, lecture_id, current_user.id)

    transcript_data = None
    if lecture.transcript:
        transcript_data = TranscriptData(
            full_text=lecture.transcript.full_text,
            segments=lecture.transcript.segments,
            language=lecture.transcript.language,
        )

    return LectureDetailResponse(
        id=lecture.id,
        title=lecture.title,
        status=lecture.status.value,
        progress=lecture.progress,
        duration=lecture.duration,
        uploaded_at=lecture.uploaded_at,
        processed_at=lecture.processed_at,
        transcript=transcript_data,
        notes=lecture.note.content if lecture.note else None,
        key_concepts=lecture.note.key_concepts if lecture.note else [],
        flashcards=[FlashcardResponse.model_validate(fc) for fc in lecture.flashcards],
        mcqs=[MCQResponse.model_validate(m) for m in lecture.mcqs],
        resources=[ResourceResponse.model_validate(r) for r in lecture.resources],
    )


@router.delete("/{lecture_id}", status_code=status.HTTP_200_OK)
def delete_lecture(
    lecture_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lecture = _get_lecture_or_404(db, lecture_id, current_user.id)

    try:
        storage_service.delete_audio(lecture.s3_key)
    except Exception as e:
        logger.warning("Audio delete failed for %s (non-fatal): %s", lecture_id, e)

    db.delete(lecture)
    db.commit()
    return {"message": f"Lecture '{lecture.title}' deleted successfully."}


# ── Helpers ────────────────────────────────────────────────────────────────

def _get_lecture_or_404(db: Session, lecture_id: str, user_id: str) -> Lecture:
    lecture = (
        db.query(Lecture)
        .filter(Lecture.id == lecture_id, Lecture.user_id == user_id)
        .first()
    )
    if not lecture:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lecture not found.")
    return lecture
