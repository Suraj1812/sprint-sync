"""Pydantic schemas for the AI platform."""

from uuid import UUID
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ChatMessageSchema(BaseModel):
    role: str
    content: str
    name: str | None = None


class ChatRequest(BaseModel):
    message: str
    conversation_id: UUID | None = None
    provider: str | None = None
    model: str | None = None
    prompt: str | None = None
    prompt_variables: dict[str, Any] | None = None
    use_rag: bool = False
    tools: list[str] | None = None
    stream: bool = False


class ChatResponse(BaseModel):
    content: str
    finish_reason: str | None = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: int = 0
    provider: str
    model: str


class StreamChunk(BaseModel):
    content: str = ""
    finish_reason: str | None = None


class PromptCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    system: str | None = None
    user_template: str = Field(..., min_length=1)
    variables: list[str] = Field(default_factory=list)


class PromptVersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    prompt_id: UUID
    version: int
    system: str | None
    user_template: str
    created_at: datetime


class PromptRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    is_active: bool
    default_version_id: UUID | None
    variables: list[str]
    created_at: datetime


class ConversationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str | None
    provider: str
    model: str
    created_at: datetime


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    conversation_id: UUID
    role: str
    content: str
    latency_ms: int | None
    created_at: datetime


class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=1)
    source: str = Field(..., min_length=1)
    text: str = Field(..., min_length=1)
    provider: str = "openai"
    model: str = "text-embedding-3-small"


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    source: str
    created_at: datetime


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = 5


class SearchResult(BaseModel):
    id: str
    content: str
    score: float
    metadata: dict[str, Any] | None = None


class EmbedRequest(BaseModel):
    inputs: list[str] = Field(..., min_length=1)
    provider: str = "openai"
    model: str = "text-embedding-3-small"


class UsageStats(BaseModel):
    total_cost_30d: float
    total_tokens_30d: int


class ToolList(BaseModel):
    tools: list[dict[str, Any]]
