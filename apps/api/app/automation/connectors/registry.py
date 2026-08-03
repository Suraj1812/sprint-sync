"""Connector registry."""

from app.automation.connectors.base import IntegrationConnector
from app.automation.connectors.github import GitHubConnector
from app.automation.connectors.slack import SlackConnector


class ConnectorRegistry:
    _connectors: dict[str, type[IntegrationConnector]] = {
        "slack": SlackConnector,
        "github": GitHubConnector,
    }

    @classmethod
    def register(cls, name: str, impl: type[IntegrationConnector]) -> None:
        cls._connectors[name] = impl

    @classmethod
    def get(cls, name: str) -> IntegrationConnector:
        impl = cls._connectors.get(name)
        if not impl:
            raise ValueError(f"Unknown connector: {name}")
        return impl()

    @classmethod
    def list(cls) -> list[str]:
        return list(cls._connectors.keys())


connector_registry = ConnectorRegistry()
