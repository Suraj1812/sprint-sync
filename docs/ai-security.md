# AI Security Guide

## Guardrails

- **Input validation** — `Guardrails.validate_input` blocks known prompt-injection markers.
- **Output filtering** — `Guardrails.filter_output` strips and normalizes responses.
- **Sensitive data redaction** — SSN and credit-card patterns are redacted.
- **RAG context filtering** — chunks below a 0.5 cosine threshold are dropped.
- **Tool permissions** — `ToolExecutor.list_schemas` and `execute` check role permissions.
- **Rate limiting** — endpoints use `slowapi`; add per-user and per-provider budgets in `CostService`.

## Secrets

Provider API keys are read from environment variables and are never logged or returned.

## Recommended Hardening

1. Add a content-moderation step for user-facing outputs.
2. Per-user daily token and cost budgets.
3. IP and behavioral abuse detection.
4. Dedicated review queue for high-risk tool calls.
