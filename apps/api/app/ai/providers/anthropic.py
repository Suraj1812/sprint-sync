"""Anthropic provider implementation using httpx."""

import json
import time
from collections.abc import AsyncIterator
from typing import Any

import httpx

from app.ai.providers.base import (
    AIProvider,
    ChatRequest,
    ChatResponse,
    ChatMessage,
    EmbeddingRequest,
    EmbeddingResponse,
    StreamChunk,
)
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("ai.anthropic")


def _estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


class AnthropicProvider(AIProvider):
    name = "anthropic"

    def __init__(self) -> None:
        settings = get_settings()
        self._api_key = settings.anthropic_api_key or ""
        self._base_url = settings.anthropic_base_url
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={
                "x-api-key": self._api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            timeout=120.0,
        )

    def estimate_tokens(self, text: str) -> int:
        return _estimate_tokens(text)

    async def health(self) -> dict[str, Any]:
        return {"provider": self.name, "ok": bool(self._api_key)}

    def _to_anthropic_messages(
        self, messages: list[ChatMessage]
    ) -> tuple[str | None, list[dict[str, Any]]]:
        system: str | None = None
        out: list[dict[str, Any]] = []
        for m in messages:
            if m.role == "system":
                system = m.content
            else:
                out.append({"role": m.role, "content": m.content})
        return system, out

    async def chat(self, request: ChatRequest) -> ChatResponse:
        start = time.monotonic()
        system, messages = self._to_anthropic_messages(request.messages)
        payload: dict[str, Any] = {
            "model": request.model,
            "messages": messages,
            "max_tokens": request.max_tokens or 1024,
            "temperature": request.temperature,
        }
        if system:
            payload["system"] = system

        response = await self._client.post("/messages", json=payload)
        response.raise_for_status()
        data = response.json()

        content_text = ""
        for block in data.get("content", []):
            if block["type"] == "text":
                content_text += block["text"]

        usage = data.get("usage", {})
        latency_ms = int((time.monotonic() - start) * 1000)

        return ChatResponse(
            content=content_text,
            prompt_tokens=usage.get("input_tokens", 0),
            completion_tokens=usage.get("output_tokens", 0),
            total_tokens=usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
            latency_ms=latency_ms,
            model=request.model,
            provider=self.name,
            finish_reason=data.get("stop_reason"),
        )

    async def stream_chat(self, request: ChatRequest) -> AsyncIterator[StreamChunk]:
        system, messages = self._to_anthropic_messages(request.messages)
        payload: dict[str, Any] = {
            "model": request.model,
            "messages": messages,
            "max_tokens": request.max_tokens or 1024,
            "temperature": request.temperature,
            "stream": True,
        }
        if system:
            payload["system"] = system

        async with self._client.stream(
            "POST",
            "/messages",
            json=payload,
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line.startswith("data: "):
                    continue
                data = line[6:]
                if data == "[DONE]":
                    break
                try:
                    event = json.loads(data)
                    if event["type"] == "content_block_delta":
                        delta = event.get("delta", {})
                        if delta.get("type") == "text_delta":
                            yield StreamChunk(content=delta.get("text") or "")
                except (json.JSONDecodeError, KeyError):
                    logger.warning("Malformed stream chunk", chunk=data)

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        start = time.monotonic()
        total_tokens = sum(self.estimate_tokens(t) for t in request.inputs)
        latency_ms = int((time.monotonic() - start) * 1000)
        # Anthropic does not provide embeddings at the time of writing; return zero vectors.
        logger.warning("Anthropic embeddings not supported; returning zero vectors")
        return EmbeddingResponse(
            embeddings=[[0.0] * 1536 for _ in request.inputs],
            total_tokens=total_tokens,
            latency_ms=latency_ms,
            model=request.model,
            provider=self.name,
        )
