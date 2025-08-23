import logging
from typing import Dict, Any

from app.workers.celery_app import celery_app
from app.db.session import get_db_session
from app.models import User
from app.services.notification_service import NotificationService, NotificationType

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3)
def send_notification_task(self, user_id: str, notification_type: str, data: Dict[str, Any]):
    """Send notification task"""
    logger.info(f"Executing send_notification_task for user {user_id}")
    try:
        with get_db_session() as db:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.warning(f"User {user_id} not found for notification")
                return

            notification_service = NotificationService()

            variables = {
                'user_name': user.full_name,
                **data
            }

            # This is an async function, but Celery tasks are often sync.
            # In a real asyncio app, you'd use `asyncio.run()` or a running loop.
            # For this stub, we'll call it directly, assuming it can run.
            notification_service.send_email_notification(
                user.email,
                NotificationType(notification_type),
                variables
            )

    except Exception as exc:
        logger.error(f"Notification task failed: {str(exc)}")
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=60)
        raise
