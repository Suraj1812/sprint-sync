"""Communication provider registries."""

from app.communications.providers.base import EmailProvider, PushProvider
from app.communications.providers.console import ConsoleEmailProvider
from app.communications.providers.postmark import PostmarkEmailProvider
from app.communications.providers.resend import ResendEmailProvider
from app.communications.providers.ses import AmazonSESEmailProvider
from app.communications.providers.sendgrid import SendGridEmailProvider
from app.core.config import get_settings


class EmailProviderRegistry:
    _providers: dict[str, type[EmailProvider]] = {
        "console": ConsoleEmailProvider,
        "resend": ResendEmailProvider,
        "sendgrid": SendGridEmailProvider,
        "postmark": PostmarkEmailProvider,
        "ses": AmazonSESEmailProvider,
    }

    @classmethod
    def get(cls, name: str) -> EmailProvider:
        impl = cls._providers.get(name)
        if not impl:
            raise ValueError(f"Unknown email provider: {name}")
        return impl()

    @classmethod
    def default(cls) -> EmailProvider:
        settings = get_settings()
        return cls.get(settings.email_provider)

    @classmethod
    def list(cls) -> list[str]:
        return list(cls._providers.keys())


class PushProviderRegistry:
    _providers: dict[str, type[PushProvider]] = {}

    @classmethod
    def get(cls, name: str) -> PushProvider:
        impl = cls._providers.get(name)
        if not impl:
            raise ValueError(f"Unknown push provider: {name}")
        return impl()

    @classmethod
    def default(cls) -> PushProvider | None:
        settings = get_settings()
        if settings.push_provider == "none":
            return None
        return cls.get(settings.push_provider)


email_provider_registry = EmailProviderRegistry()
