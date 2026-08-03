# AI Observability

## Captured Data

- `ai_call_logs` — provider, model, operation, latency, error, metadata.
- `ai_usage` — per-call token counts, cost, status, user, conversation.
- `conversations` / `messages` — full conversation history with latency.
- `documents` / `document_chunks` — RAG corpus and embeddings.

## OpenTelemetry Integration

The `trace_ai_call` context manager is ready to wrap provider calls. In production, replace the manual `AICallLog` repository insert with an OpenTelemetry span exporter and attach token counts, model, and provider as span attributes.

## Dashboards

- `/admin/ai/usage` — 30-day cost and token totals.
- `/admin/ai/providers` — provider health status.
- Error rate, latency, and token counts are queryable from `ai_usage` and `ai_call_logs`.
