"""Amazon SES email provider placeholder."""

from typing import Any

from app.communications.providers.base import DeliveryResult, EmailMessage, EmailProvider
from app.core.exceptions import ServiceUnavailableError


class AmazonSESEmailProvider(EmailProvider):
    name = "ses"

    async def send(self, message: EmailMessage) -> DeliveryResult:
        raise ServiceUnavailableError("Amazon SES provider not yet implemented")

    async def health(self) -> dict[str, Any]:
        return {"ok": False, "error": "not implemented"}
