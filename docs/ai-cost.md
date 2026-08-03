# Cost Monitoring

## Pricing Model

`CostService.PRICING` stores approximate per-million-token prices for prompt and completion tokens. Update this table as provider pricing changes.

## Tracking

Every call to `ChatService.chat` or `stream` logs an `AIUsage` row with:

- `prompt_tokens`
- `completion_tokens`
- `total_tokens`
- `cost_usd`
- `latency_ms`
- `provider` and `model`
- `user_id` and `conversation_id`

## Budgeting

Use `AIUsageRepository.total_cost_for_user` to enforce per-user limits. Add a pre-call check in `ChatService` to reject requests that exceed a configured daily cap.
