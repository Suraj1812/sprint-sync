"""Stripe payment provider."""

import hashlib
import hmac
from typing import Any

import httpx

from app.billing.providers.base import PaymentProvider
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("billing.stripe")


class StripeProvider(PaymentProvider):
    name = "stripe"

    def __init__(self) -> None:
        settings = get_settings()
        self._secret_key = settings.stripe_secret_key or ""
        self._webhook_secret = settings.stripe_webhook_secret or ""
        self._client = httpx.AsyncClient(
            base_url="https://api.stripe.com/v1",
            auth=(self._secret_key, ""),
            timeout=60.0,
        )

    async def _request(
        self,
        method: str,
        path: str,
        *,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        response = await self._client.request(
            method,
            path,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response.raise_for_status()
        return response.json()

    async def create_customer(
        self,
        email: str,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload = {"email": email}
        if metadata:
            for key, value in metadata.items():
                payload[f"metadata[{key}]"] = str(value)
        return await self._request("POST", "/customers", data=payload)

    async def create_checkout_session(
        self,
        price_id: str,
        customer_id: str,
        *,
        success_url: str,
        cancel_url: str,
        mode: str = "subscription",
    ) -> dict[str, Any]:
        return await self._request(
            "POST",
            "/checkout/sessions",
            data={
                "mode": mode,
                "customer": customer_id,
                "line_items[0][price]": price_id,
                "line_items[0][quantity]": "1",
                "success_url": success_url,
                "cancel_url": cancel_url,
            },
        )

    async def create_portal_session(
        self,
        customer_id: str,
        *,
        return_url: str,
    ) -> dict[str, Any]:
        return await self._request(
            "POST",
            "/billing_portal/sessions",
            data={
                "customer": customer_id,
                "return_url": return_url,
            },
        )

    async def get_event(self, event_id: str) -> dict[str, Any] | None:
        try:
            return await self._request("GET", f"/events/{event_id}")
        except httpx.HTTPStatusError:
            return None

    def verify_signature(self, payload: bytes, signature: str) -> bool:
        if not self._webhook_secret:
            logger.error("Stripe webhook secret not configured")
            return False

        parts = {}
        for item in signature.split(","):
            if "=" in item:
                k, v = item.split("=", 1)
                parts[k] = v

        timestamp = parts.get("t")
        signature_hex = parts.get("v1")
        if not timestamp or not signature_hex:
            return False

        signed_payload = timestamp.encode() + b"." + payload
        expected = hmac.new(
            self._webhook_secret.encode(),
            signed_payload,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, signature_hex)
