"""Console email provider for local development."""

from typing import Any

from app.communications.providers.base import DeliveryResult, EmailMessage, EmailProvider
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("communications.console")


class ConsoleEmailProvider(EmailProvider):
    name = "console"

    async def send(self, message: EmailMessage) -> DeliveryResult:
        logger.info(
            "[EMAIL]",
            to=message.to,
            subject=message.subject,
            from_address=message.from_address,
        )
        return DeliveryResult(success=True, provider_id="console", status="sent")

    async def health(self) -> dict[str, Any]:
        return {"ok": True}
