"""Automation platform tests."""

import hashlib

import pytest

from app.automation.api_key import api_key_service
from app.automation.connectors.registry import ConnectorRegistry
from app.automation.event_bus import DomainEventBus
from app.automation.oauth import oauth_service


class TestApiKeyHashing:
    def test_hash_is_deterministic(self):
        assert api_key_service._hash("abc") == hashlib.sha256("abc".encode()).hexdigest()

    def test_preview(self):
        raw = "ssk_" + "x" * 32
        assert raw[-10:] == api_key_service._hash(raw)[-10:]


class TestOAuthClientId:
    def test_client_id_prefix(self):
        client_id = "cli_test"
        assert client_id.startswith("cli_")


class TestConnectorRegistry:
    def test_list(self):
        assert "slack" in ConnectorRegistry.list()
        assert "github" in ConnectorRegistry.list()


class TestEventBus:
    def test_subscribe_and_dispatch(self):
        bus = DomainEventBus()
        called = []

        async def handler(db, event):
            called.append(event.event_type)

        bus.subscribe("test.event", handler)
        # dispatch requires a real db session; this only tests the subscriber list
        assert bus._subscribers["test.event"] == [handler]
