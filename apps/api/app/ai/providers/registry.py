"""Provider registry and selection."""

from app.ai.providers.anthropic import AnthropicProvider
from app.ai.providers.azure import AzureOpenAIProvider
from app.ai.providers.base import AIProvider
from app.ai.providers.ollama import OllamaProvider
from app.ai.providers.openai import OpenAIProvider
from app.core.config import get_settings


class ProviderRegistry:
    _providers: dict[str, type[AIProvider]] = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "ollama": OllamaProvider,
        "azure_openai": AzureOpenAIProvider,
    }

    @classmethod
    def get(cls, name: str) -> AIProvider:
        impl = cls._providers.get(name)
        if not impl:
            raise ValueError(f"Unknown AI provider: {name}")
        return impl()

    @classmethod
    def default_provider(cls) -> AIProvider:
        settings = get_settings()
        return cls.get(settings.ai_default_provider)

    @classmethod
    def list(cls) -> list[str]:
        return list(cls._providers.keys())

    @classmethod
    def register(cls, name: str, impl: type[AIProvider]) -> None:
        cls._providers[name] = impl


provider_registry = ProviderRegistry()
