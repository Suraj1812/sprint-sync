"""Resend email provider."""

from typing import Any

import httpx

from app.communications.providers.base import DeliveryResult, EmailMessage, EmailProvider
from app.core.config import get_settings


class ResendEmailProvider(EmailProvider):
    name = "resend"

    def __init__(self) -> None:
        settings = get_settings()
        self._api_key = settings.resend_api_key or ""
        self._client = httpx.AsyncClient(
            base_url="https://api.resend.com",
            headers={"Authorization": f"Bearer {self._api_key}"},
            timeout=60.0,
        )

    async def send(self, message: EmailMessage) -> DeliveryResult:
        from_address = message.from_address or get_settings().email_from
        payload = {
            "from": from_address,
            "to": [message.to],
            "subject": message.subject,
        }
        if message.html:
            payload["html"] = message.html
        if message.text:
            payload["text"] = message.text

        try:
            response = await self._client.post("/emails", json=payload)
            response.raise_for_status()
            data = response.json()
            return DeliveryResult(
                success=True,
                provider_id=data.get("id"),
                status="sent",
                metadata=data,
            )
        except httpx.HTTPStatusError as exc:
            return DeliveryResult(
                success=False,
                status="failed",
                error=str(exc),
                metadata={"status_code": exc.response.status_code},
            )

    async def health(self) -> dict[str, Any]:
        if not self._api_key:
            return {"ok": False, "error": "missing api key"}
        return {"ok": True}
