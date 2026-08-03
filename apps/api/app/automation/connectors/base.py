"""Integration connector interface."""

from abc import ABC, abstractmethod
from typing import Any


class IntegrationConnector(ABC):
    name: str = ""

    @abstractmethod
    async def execute(self, config: dict[str, Any]) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def health(self) -> dict[str, Any]:
        raise NotImplementedError
