"""Celery app for async processing of heavy media files (transcription, diarization)."""
from celery import Celery

from app.config import settings

celery_app = Celery(
    "meetmind",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.worker.tasks"],
)

celery_app.conf.task_routes = {
    "app.worker.tasks.process_meeting": {"queue": "transcription"},
    "app.worker.tasks.run_extraction": {"queue": "extraction"},
}
