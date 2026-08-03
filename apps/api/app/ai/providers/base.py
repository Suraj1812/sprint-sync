"""Provider-agnostic AI interface."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any


@dataclass
class ChatMessage:
    role: str
    content: str
    name: str | None = None


@dataclass
class ChatRequest:
    model: str
    messages: list[ChatMessage]
    temperature: float = 0.7
    max_tokens: int | None = None
    tools: list[dict[str, Any]] | None = None
    stream: bool = False


@dataclass
class ChatResponse:
    content: str
    tool_calls: list[dict[str, Any]] | None = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: int = 0
    model: str = ""
    provider: str = ""
    finish_reason: str | None = None


@dataclass
class StreamChunk:
    content: str = ""
    tool_calls: list[dict[str, Any]] | None = None
    finish_reason: str | None = None


@dataclass
class EmbeddingRequest:
    model: str
    inputs: list[str]


@dataclass
class EmbeddingResponse:
    embeddings: list[list[float]]
    total_tokens: int = 0
    latency_ms: int = 0
    model: str = ""
    provider: str = ""


class AIProvider(ABC):
    name: str = ""

    @abstractmethod
    async def chat(self, request: ChatRequest) -> ChatResponse:
        raise NotImplementedError

    @abstractmethod
    async def stream_chat(self, request: ChatRequest) -> AsyncIterator[StreamChunk]:
        raise NotImplementedError

    @abstractmethod
    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        raise NotImplementedError

    @abstractmethod
    async def health(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def estimate_tokens(self, text: str) -> int:
        raise NotImplementedError
