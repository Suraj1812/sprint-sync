"""Communication provider interfaces."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class EmailMessage:
    to: str
    subject: str
    html: str | None = None
    text: str | None = None
    from_address: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class PushMessage:
    device_token: str
    title: str
    body: str
    data: dict[str, Any] | None = None
    priority: str = "normal"


@dataclass
class DeliveryResult:
    success: bool
    provider_id: str | None = None
    status: str = "sent"
    error: str | None = None
    metadata: dict[str, Any] | None = None


class EmailProvider(ABC):
    name: str = ""

    @abstractmethod
    async def send(self, message: EmailMessage) -> DeliveryResult:
        raise NotImplementedError

    @abstractmethod
    async def health(self) -> dict[str, Any]:
        raise NotImplementedError


class PushProvider(ABC):
    name: str = ""

    @abstractmethod
    async def send(self, message: PushMessage) -> DeliveryResult:
        raise NotImplementedError

    @abstractmethod
    async def health(self) -> dict[str, Any]:
        raise NotImplementedError
