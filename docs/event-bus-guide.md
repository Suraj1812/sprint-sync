# Event Bus Guide

## Naming

Use reverse-domain style: `resource.action`.

Examples:
- `user.registered`
- `organization.created`
- `billing.invoice.paid`
- `ai.task.completed`
- `workflow.run.completed`

## Versioning

`DomainEvent.version` starts at `1`. New schema versions increment the number and subscribers must handle both.

## Publishing

```python
await domain_event_bus.publish(
    db,
    "workspace.created",
    {"workspace_id": str(ws.id), "user_id": str(user.id)},
    tenant_id=org.id,
    correlation_id=correlation_id,
)
```

## Subscribing

```python
domain_event_bus.subscribe("user.registered", on_user_registered)
```

Handlers are called synchronously during `publish`. For high volume, move to a Celery task.

## Correlation and Idempotency

- `correlation_id` ties related events together.
- Consumers should guard against duplicate processing using `event.id`.
- `processed_at` and `status` track lifecycle.
