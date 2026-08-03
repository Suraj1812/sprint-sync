"""Billing platform unit tests."""

import pytest

from app.billing.providers.registry import payment_provider_registry
from app.billing.providers.stripe import StripeProvider
from app.core.exceptions import ServiceUnavailableError


class TestPaymentProviderRegistry:
    def test_lists_providers(self):
        providers = payment_provider_registry.list()
        assert "stripe" in providers
        assert "paddle" in providers
        assert "razorpay" in providers

    def test_unknown_provider_raises(self):
        with pytest.raises(ValueError):
            payment_provider_registry.get("unknown")

    def test_default_provider_is_stripe(self):
        provider = payment_provider_registry.get("stripe")
        assert isinstance(provider, StripeProvider)


class TestStubProviders:
    @pytest.mark.asyncio
    async def test_paddle_raises(self):
        provider = payment_provider_registry.get("paddle")
        with pytest.raises(ServiceUnavailableError):
            await provider.create_customer("test@example.com")

    @pytest.mark.asyncio
    async def test_razorpay_raises(self):
        provider = payment_provider_registry.get("razorpay")
        with pytest.raises(ServiceUnavailableError):
            await provider.create_customer("test@example.com")
