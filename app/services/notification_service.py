import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from enum import Enum

from app.core.config import settings

logger = logging.getLogger(__name__)

class NotificationType(str, Enum):
    DOCUMENT_PROCESSED = "document_processed"
    DOCUMENT_FAILED = "document_failed"
    SUBSCRIPTION_EXPIRED = "subscription_expired"
    USAGE_LIMIT_WARNING = "usage_limit_warning"
    SECURITY_ALERT = "security_alert"

@dataclass
class NotificationTemplate:
    subject: str
    text_body: str
    html_body: str
    variables: List[str]

class NotificationService:
    def __init__(self):
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[NotificationType, NotificationTemplate]:
        # In a real app, these might be loaded from a file or database
        return {
            NotificationType.DOCUMENT_PROCESSED: NotificationTemplate(
                subject="Dokument został przetworzony - {document_name}",
                text_body="Witaj {user_name},\n\nTwój dokument \"{document_name}\" został pomyślnie przetworzony.",
                html_body="<p>Witaj {user_name},</p><p>Twój dokument \"<strong>{document_name}</strong>\" został pomyślnie przetworzony.</p>",
                variables=["user_name", "document_name"]
            ),
            NotificationType.USAGE_LIMIT_WARNING: NotificationTemplate(
                subject="Ostrzeżenie - zbliżasz się do limitu zapytań",
                text_body="Witaj {user_name},\n\nWykorzystałeś już {usage_percentage}% miesięcznego limitu zapytań.",
                html_body="<p>Witaj {user_name},</p><p>Wykorzystałeś już <strong>{usage_percentage}%</strong> miesięcznego limitu zapytań.</p>",
                variables=["user_name", "usage_percentage"]
            )
            # Add other templates here
        }

    async def send_email_notification(
        self,
        user_email: str,
        notification_type: NotificationType,
        variables: Dict[str, Any]
    ):
        if not all(k in variables for k in self.templates[notification_type].variables):
            logger.error(f"Missing variables for notification {notification_type}")
            return

        template = self.templates[notification_type]

        subject = template.subject.format(**variables)
        text_body = template.text_body.format(**variables)
        html_body = template.html_body.format(**variables)

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = settings.FROM_EMAIL
        msg['To'] = user_email

        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))

        # This is a stub for sending email. A real implementation would connect to an SMTP server.
        if not (settings.SMTP_HOST and settings.SMTP_PORT):
            logger.warning(f"SMTP not configured. Pretending to send email to {user_email}:\nSubject: {subject}\nBody: {text_body}")
            return

        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                    server.starttls()
                    server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.send_message(msg)
            logger.info(f"Email sent successfully to {user_email}")
        except Exception as e:
            logger.error(f"Failed to send email to {user_email}: {str(e)}")
            raise
