"""Razorpay provider placeholder."""

from typing import Any

from app.billing.providers.base import PaymentProvider
from app.core.config import get_settings
from app.core.exceptions import ServiceUnavailableError


class RazorpayProvider(PaymentProvider):
    name = "razorpay"

    def __init__(self) -> None:
        settings = get_settings()
        self._key_id = settings.razorpay_key_id
        self._key_secret = settings.razorpay_key_secret
        self._webhook_secret = settings.razorpay_webhook_secret

    async def create_customer(
        self,
        email: str,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        raise ServiceUnavailableError("Razorpay provider not yet implemented")

    async def create_checkout_session(
        self,
        price_id: str,
        customer_id: str,
        *,
        success_url: str,
        cancel_url: str,
        mode: str = "subscription",
    ) -> dict[str, Any]:
        raise ServiceUnavailableError("Razorpay provider not yet implemented")

    async def create_portal_session(
        self,
        customer_id: str,
        *,
        return_url: str,
    ) -> dict[str, Any]:
        raise ServiceUnavailableError("Razorpay provider not yet implemented")

    async def get_event(self, event_id: str) -> dict[str, Any] | None:
        raise ServiceUnavailableError("Razorpay provider not yet implemented")

    def verify_signature(self, payload: bytes, signature: str) -> bool:
        raise ServiceUnavailableError("Razorpay provider not yet implemented")
