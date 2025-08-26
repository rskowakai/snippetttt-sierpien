from celery import Celery
from .config import settings

celery_app = Celery(
    "tasks",
    broker=settings.REDIS_BROKER_URL,
    backend=settings.REDIS_BROKER_URL,
    include=["app.workers.document_processor", "app.workers.transcription"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Warsaw",
    enable_utc=True,
    task_track_started=True,
)
