"""Ollama local model provider."""

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


def _estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


class OllamaProvider(AIProvider):
    name = "ollama"

    def __init__(self) -> None:
        settings = get_settings()
        self._base_url = settings.ollama_base_url
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=120.0,
        )

    def estimate_tokens(self, text: str) -> int:
        return _estimate_tokens(text)

    async def health(self) -> dict[str, Any]:
        try:
            response = await self._client.get("/api/tags")
            return {"provider": self.name, "ok": response.status_code == 200}
        except httpx.RequestError:
            return {"provider": self.name, "ok": False}

    async def chat(self, request: ChatRequest) -> ChatResponse:
        start = time.monotonic()
        prompt = "\n".join(f"{m.role}: {m.content}" for m in request.messages)
        response = await self._client.post(
            "/api/generate",
            json={
                "model": request.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": request.temperature},
            },
        )
        response.raise_for_status()
        data = response.json()
        latency_ms = int((time.monotonic() - start) * 1000)

        total_tokens = _estimate_tokens(prompt) + _estimate_tokens(data.get("response", ""))
        return ChatResponse(
            content=data.get("response", ""),
            prompt_tokens=_estimate_tokens(prompt),
            completion_tokens=_estimate_tokens(data.get("response", "")),
            total_tokens=total_tokens,
            latency_ms=latency_ms,
            model=request.model,
            provider=self.name,
        )

    async def stream_chat(self, request: ChatRequest) -> AsyncIterator[StreamChunk]:
        prompt = "\n".join(f"{m.role}: {m.content}" for m in request.messages)
        response = await self._client.post(
            "/api/generate",
            json={
                "model": request.model,
                "prompt": prompt,
                "stream": True,
                "options": {"temperature": request.temperature},
            },
        )
        response.raise_for_status()
        async for line in response.aiter_lines():
            try:
                data = json.loads(line)
                yield StreamChunk(
                    content=data.get("response", ""),
                    finish_reason="stop" if data.get("done") else None,
                )
            except json.JSONDecodeError:
                continue

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        start = time.monotonic()
        embeddings: list[list[float]] = []
        for text in request.inputs:
            response = await self._client.post(
                "/api/embeddings",
                json={"model": request.model, "prompt": text},
            )
            response.raise_for_status()
            data = response.json()
            embeddings.append(data.get("embedding", []))
        latency_ms = int((time.monotonic() - start) * 1000)

        total_tokens = sum(_estimate_tokens(t) for t in request.inputs)
        return EmbeddingResponse(
            embeddings=embeddings,
            total_tokens=total_tokens,
            latency_ms=latency_ms,
            model=request.model,
            provider=self.name,
        )
