"""OpenAI provider implementation using httpx."""

import json
import time
from collections.abc import AsyncIterator
from typing import Any

import httpx

from app.ai.providers.base import (
    AIProvider,
    ChatRequest,
    ChatResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    StreamChunk,
)
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("ai.openai")


def _estimate_tokens(text: str) -> int:
    """Rough token estimator: ~4 characters per token."""
    return max(1, len(text) // 4)


class OpenAIProvider(AIProvider):
    name = "openai"

    def __init__(self) -> None:
        settings = get_settings()
        self._api_key = settings.openai_api_key or ""
        self._base_url = settings.openai_base_url
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"},
            timeout=120.0,
        )

    def estimate_tokens(self, text: str) -> int:
        return _estimate_tokens(text)

    async def health(self) -> dict[str, Any]:
        return {"provider": self.name, "ok": bool(self._api_key)}

    async def chat(self, request: ChatRequest) -> ChatResponse:
        start = time.monotonic()
        payload: dict[str, Any] = {
            "model": request.model,
            "messages": [
                {"role": m.role, "content": m.content, **({"name": m.name} if m.name else {})}
                for m in request.messages
            ],
            "temperature": request.temperature,
        }
        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens
        if request.tools:
            payload["tools"] = request.tools

        response = await self._client.post("/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()

        choice = data["choices"][0]
        message = choice["message"]
        usage = data.get("usage", {})
        latency_ms = int((time.monotonic() - start) * 1000)

        return ChatResponse(
            content=message.get("content") or "",
            tool_calls=message.get("tool_calls"),
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            total_tokens=usage.get("total_tokens", 0),
            latency_ms=latency_ms,
            model=request.model,
            provider=self.name,
            finish_reason=choice.get("finish_reason"),
        )

    async def stream_chat(self, request: ChatRequest) -> AsyncIterator[StreamChunk]:
        payload: dict[str, Any] = {
            "model": request.model,
            "messages": [
                {"role": m.role, "content": m.content}
                for m in request.messages
            ],
            "temperature": request.temperature,
            "stream": True,
        }
        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens

        async with self._client.stream(
            "POST",
            "/chat/completions",
            json=payload,
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        delta = chunk["choices"][0].get("delta", {})
                        yield StreamChunk(
                            content=delta.get("content") or "",
                            finish_reason=chunk["choices"][0].get("finish_reason"),
                        )
                    except (json.JSONDecodeError, KeyError):
                        logger.warning("Malformed stream chunk", chunk=data)

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        start = time.monotonic()
        total_tokens = sum(self.estimate_tokens(t) for t in request.inputs)
        response = await self._client.post(
            "/embeddings",
            json={"model": request.model, "input": request.inputs},
        )
        response.raise_for_status()
        data = response.json()
        embeddings = [item["embedding"] for item in data["data"]]
        latency_ms = int((time.monotonic() - start) * 1000)

        return EmbeddingResponse(
            embeddings=embeddings,
            total_tokens=total_tokens,
            latency_ms=latency_ms,
            model=request.model,
            provider=self.name,
        )
