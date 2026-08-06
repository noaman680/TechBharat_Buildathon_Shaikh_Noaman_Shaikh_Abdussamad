"""Celery application configuration."""
from celery import Celery
from app.config import settings

celery_app = Celery(
    "meetmind",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.worker.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_routes={
        "app.worker.tasks.transcribe_meeting": {"queue": "gpu"},
        "app.worker.tasks.process_meeting": {"queue": "llm"},
        "app.worker.tasks.execute_integration": {"queue": "integration"},
    },
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)
