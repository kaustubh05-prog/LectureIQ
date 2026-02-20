from celery import Celery
from app.config import settings

celery_app = Celery(
    "lectureiq",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.process_lecture"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,   # One task at a time (Whisper is heavy)
    task_routes={
        "app.tasks.process_lecture.*": {"queue": "lectures"},
    },
)
