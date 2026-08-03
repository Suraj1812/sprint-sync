"""Postmark email provider."""

from typing import Any

import httpx

from app.communications.providers.base import DeliveryResult, EmailMessage, EmailProvider
from app.core.config import get_settings


class PostmarkEmailProvider(EmailProvider):
    name = "postmark"

    def __init__(self) -> None:
        settings = get_settings()
        self._api_key = settings.postmark_api_key or ""
        self._client = httpx.AsyncClient(
            base_url="https://api.postmarkapp.com",
            headers={
                "X-Postmark-Server-Token": self._api_key,
                "Content-Type": "application/json",
            },
            timeout=60.0,
        )

    async def send(self, message: EmailMessage) -> DeliveryResult:
        from_address = message.from_address or get_settings().email_from
        payload = {
            "From": from_address,
            "To": message.to,
            "Subject": message.subject,
        }
        if message.html:
            payload["HtmlBody"] = message.html
        if message.text:
            payload["TextBody"] = message.text

        try:
            response = await self._client.post("/email", json=payload)
            response.raise_for_status()
            data = response.json()
            return DeliveryResult(
                success=True,
                provider_id=str(data.get("MessageID")),
                status="sent",
                metadata=data,
            )
        except httpx.HTTPStatusError as exc:
            return DeliveryResult(success=False, status="failed", error=str(exc))

    async def health(self) -> dict[str, Any]:
        if not self._api_key:
            return {"ok": False, "error": "missing api key"}
        return {"ok": True}
