# Provider Integration Guide

## Supported Providers

- **OpenAI** (`openai`) — chat completions, streaming, embeddings.
- **Anthropic** (`anthropic`) — Claude messages, streaming; embeddings not supported.
- **Ollama** (`ollama`) — local open models via `/api/generate` and `/api/embeddings`.
- **Azure OpenAI** (`azure_openai`) — placeholder; implement in `AzureOpenAIProvider`.

## Adding a Provider

1. Create `app/ai/providers/<name>.py`.
2. Subclass `AIProvider` and implement `chat`, `stream_chat`, `embed`, `health`, `estimate_tokens`.
3. Register in `app/ai/providers/registry.py`.
4. Add pricing to `CostService.PRICING`.
5. Set environment variables and `AI_DEFAULT_PROVIDER`.

## Configuration

```bash
AI_DEFAULT_PROVIDER=openai
AI_DEFAULT_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
ANTHROPIC_API_KEY=sk-ant-...
OLLAMA_BASE_URL=http://localhost:11434
```
