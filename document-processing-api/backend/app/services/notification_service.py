import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class NotificationService:
    @staticmethod
    async def send_notification(
        recipient: str,
        message: str,
        metadata: Dict[str, Any]
    ):
        """
        Sends a notification. This is a placeholder.
        In a real app, this would integrate with an email/SMS service
        and use the notification_worker Celery task.
        """
        logger.info(f"Sending notification to {recipient}: {message}")
        logger.info(f"Metadata: {metadata}")
        # In a real app, you would probably do:
        # from ..workers.notification_worker import send_email_task
        # send_email_task.delay(recipient, message, metadata)
        pass

notification_service = NotificationService()
