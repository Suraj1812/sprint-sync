"""SendGrid email provider."""

from typing import Any

import httpx

from app.communications.providers.base import DeliveryResult, EmailMessage, EmailProvider
from app.core.config import get_settings


class SendGridEmailProvider(EmailProvider):
    name = "sendgrid"

    def __init__(self) -> None:
        settings = get_settings()
        self._api_key = settings.sendgrid_api_key or ""
        self._client = httpx.AsyncClient(
            base_url="https://api.sendgrid.com/v3",
            headers={"Authorization": f"Bearer {self._api_key}"},
            timeout=60.0,
        )

    async def send(self, message: EmailMessage) -> DeliveryResult:
        from_address = message.from_address or get_settings().email_from
        payload = {
            "personalizations": [{"to": [{"email": message.to}]}],
            "from": {"email": from_address},
            "subject": message.subject,
            "content": [],
        }
        if message.text:
            payload["content"].append({"type": "text/plain", "value": message.text})
        if message.html:
            payload["content"].append({"type": "text/html", "value": message.html})

        try:
            response = await self._client.post("/mail/send", json=payload)
            response.raise_for_status()
            return DeliveryResult(success=True, status="sent")
        except httpx.HTTPStatusError as exc:
            return DeliveryResult(success=False, status="failed", error=str(exc))

    async def health(self) -> dict[str, Any]:
        if not self._api_key:
            return {"ok": False, "error": "missing api key"}
        return {"ok": True}
