"""Payment provider registry."""

from app.billing.providers.base import PaymentProvider
from app.billing.providers.paddle import PaddleProvider
from app.billing.providers.razorpay import RazorpayProvider
from app.billing.providers.stripe import StripeProvider
from app.core.config import get_settings


class PaymentProviderRegistry:
    _providers: dict[str, type[PaymentProvider]] = {
        "stripe": StripeProvider,
        "paddle": PaddleProvider,
        "razorpay": RazorpayProvider,
    }

    @classmethod
    def get(cls, name: str) -> PaymentProvider:
        impl = cls._providers.get(name)
        if not impl:
            raise ValueError(f"Unknown payment provider: {name}")
        return impl()

    @classmethod
    def default(cls) -> PaymentProvider:
        settings = get_settings()
        return cls.get(settings.billing_provider)

    @classmethod
    def list(cls) -> list[str]:
        return list(cls._providers.keys())

    @classmethod
    def register(cls, name: str, impl: type[PaymentProvider]) -> None:
        cls._providers[name] = impl


payment_provider_registry = PaymentProviderRegistry()
