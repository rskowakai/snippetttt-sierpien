from celery import Celery
from celery.signals import task_prerun, task_postrun, task_failure
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

celery_app = Celery(
    "prawoasystent",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.workers.document_processor_worker",
        "app.workers.notification_worker"
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    worker_prefetch_multiplier=1,
    task_routes={
        "app.workers.document_processor_worker.*": {"queue": "documents"},
        "app.workers.notification_worker.*": {"queue": "notifications"}
    },
)

@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, **kwargs):
    logger.info(f"Task {task.name}[{task_id}] started")

@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, state=None, **kwargs):
    logger.info(f"Task {task.name}[{task_id}] completed with state: {state}")

@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, traceback=None, **kwargs):
    logger.error(f"Task {sender.name}[{task_id}] failed: {exception}")
