"""Communication platform tests."""

import pytest
from string import Template

from app.communications.providers.base import DeliveryResult
from app.communications.providers.console import ConsoleEmailProvider


class TestTemplateRendering:
    def test_basic_substitution(self):
        template = Template("Hello {{ name }}")
        assert template.safe_substitute({"name": "Alice"}) == "Hello Alice"

    def test_missing_variable(self):
        template = Template("Hello {{ name }}")
        assert template.safe_substitute({}) == "Hello {{ name }}"


class TestConsoleProvider:
    async def test_send(self):
        from app.communications.providers.base import EmailMessage
        provider = ConsoleEmailProvider()
        result = await provider.send(
            EmailMessage(
                to="test@example.com",
                subject="Test",
                html="<p>hi</p>",
            )
        )
        assert result.success
        assert result.status == "sent"
