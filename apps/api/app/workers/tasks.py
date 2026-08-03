"""Background task examples for email, notifications, and long-running work."""

from app.core.logging import get_logger
from app.workers.celery_app import celery_app

logger = get_logger("workers.tasks")


@celery_app.task(bind=True)
def send_email(self, to: str, subject: str, body: str) -> dict:
    """Queue an email to be sent by the configured provider."""
    logger.info(
        "email_task_enqueued",
        task_id=self.request.id,
        to=to,
        subject=subject,
    )
    # Real implementations should hand off to an email provider (SMTP, SES,
    # Postmark, etc.) without logging the message body or tokens.
    return {"status": "queued", "to": to}


@celery_app.task
def send_notification(user_id: str, message: str) -> dict:
    """Queue an in-app or push notification."""
    logger.info("notification_task_enqueued", user_id=user_id, message=message)
    return {"status": "queued", "user_id": user_id}


@celery_app.task(bind=True)
def long_running_job(self, payload: dict) -> dict:
    """Generic long-running job hook for reports, imports, or exports."""
    logger.info("long_running_job_started", task_id=self.request.id)
    # Worker implementation is intentionally left to domain-specific tasks
    # (reports, imports, exports, data migrations, etc.).
    return {"status": "completed"}
