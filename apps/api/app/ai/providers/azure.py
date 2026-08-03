"""Azure OpenAI provider placeholder."""

from collections.abc import AsyncIterator
from typing import Any

from app.ai.providers.base import (
    AIProvider,
    ChatRequest,
    ChatResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    StreamChunk,
)
from app.core.config import get_settings
from app.core.exceptions import ServiceUnavailableError


class AzureOpenAIProvider(AIProvider):
    name = "azure_openai"

    def __init__(self) -> None:
        settings = get_settings()
        self._endpoint = settings.azure_openai_endpoint
        self._key = settings.azure_openai_key

    def estimate_tokens(self, text: str) -> int:
        return max(1, len(text) // 4)

    async def health(self) -> dict[str, Any]:
        return {"provider": self.name, "ok": bool(self._endpoint and self._key)}

    async def chat(self, request: ChatRequest) -> ChatResponse:
        raise ServiceUnavailableError(
            "Azure OpenAI provider is configured but not yet implemented"
        )

    async def stream_chat(self, request: ChatRequest) -> AsyncIterator[StreamChunk]:
        raise ServiceUnavailableError(
            "Azure OpenAI provider is configured but not yet implemented"
        )

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        raise ServiceUnavailableError(
            "Azure OpenAI provider is configured but not yet implemented"
        )
