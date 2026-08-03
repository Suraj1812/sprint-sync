"""Provider-agnostic payment interface."""

from abc import ABC, abstractmethod
from typing import Any


class PaymentProvider(ABC):
    name: str = ""

    @abstractmethod
    async def create_customer(
        self,
        email: str,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def create_checkout_session(
        self,
        price_id: str,
        customer_id: str,
        *,
        success_url: str,
        cancel_url: str,
        mode: str = "subscription",
    ) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def create_portal_session(
        self,
        customer_id: str,
        *,
        return_url: str,
    ) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def get_event(self, event_id: str) -> dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    def verify_signature(self, payload: bytes, signature: str) -> bool:
        raise NotImplementedError
