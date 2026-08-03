# Entitlements Guide

## Model

`Entitlement` links a `plan_id` to a `feature`, `limit`, and `value`.

## Features

- `ai_tokens` — monthly token allowance.
- `seats` — number of allowed seats.
- `storage` — storage in MB/GB.
- `api_calls` — API request quota.
- `premium_support` — enabled/disabled via `value`.

## Application Checks

Always check `entitlement_service.can_use(...)` or `entitlement_service.has_feature(...)` rather than comparing `plan.name`.

```python
allowed = await entitlement_service.can_use(
    db,
    customer_id,
    feature="ai_tokens",
    metric="ai_tokens",
    quantity=1000,
)
```

## Free Plan

If a user has no active subscription, the system falls back to the `free` plan entitlements.
