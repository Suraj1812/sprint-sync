# AI Platform Architecture

## Overview

The AI platform is a provider-agnostic layer that exposes clean interfaces for chat, embeddings, RAG, tool calling, prompt management, cost tracking, and observability. Business features consume it through `app/ai` services, never through provider-specific SDKs.

## Layers

```
apps/web/app/admin/ai   → admin management UI
app/api/v1/ai           → REST / SSE endpoints
app/ai/services         → orchestration (chat, RAG, tools, cost, guardrails)
app/ai/providers        → provider implementations (OpenAI, Anthropic, Ollama, Azure)
app/models              → conversations, prompts, documents, usage, call logs
```

## Services

- **ChatService** — picks a provider, builds messages, optionally calls RAG, executes tools, persists conversation, logs cost.
- **PromptService** — versioned prompt templates with variable interpolation.
- **ConversationService** — message history and session continuity.
- **RetrievalService** — document chunking, embedding, and semantic search.
- **EmbeddingService** — provider-agnostic embeddings and cosine similarity.
- **ToolExecutor** — function registry with permission checks.
- **CostService** — token and cost tracking.
- **Guardrails** — input validation, output filtering, prompt-injection mitigation.

## Provider Abstraction

All providers implement `AIProvider` (`chat`, `stream_chat`, `embed`, `health`, `estimate_tokens`). Switching providers is a configuration change via `AI_DEFAULT_PROVIDER`.
