from app.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, name="app.tasks.process_lecture.run")
def process_lecture_task(self, lecture_id: str):
    """Main pipeline task — implemented in Phase 1."""
    logger.info(f"[STUB] Processing lecture: {lecture_id}")
    return {"status": "stub"}
