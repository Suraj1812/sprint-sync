# Communication Architecture

## Goal

A centralized, provider-agnostic messaging platform. No business feature sends emails or push directly. They publish events to the communication bus.

## Components

```
Business Service
   │
   ▼
event_bus.publish(event_type, payload)
   │
   ▼
EventBusService ──► EmailService / NotificationService
   │                   │
   ▼                   ▼
Provider Registry   In-app notification center
   │
   ▼
Resend / SendGrid / SES / Postmark
```

## Channels

- **Email** — fully implemented with provider abstraction.
- **In-app notifications** — notification center with read/ unread, archive, categories.
- **Push / SMS / Webhook** — provider interfaces and registries ready; implementations stubbed.

## Tenant Awareness

Every communication event carries an optional `tenant_id`. In-app notifications store `organization_id` and `workspace_id`. Audit logs include tenant context.

## Event-Driven Flow

1. A service (auth, billing, tenancy) calls `event_bus.publish`.
2. The event is persisted with `status = pending`.
3. `dispatch` evaluates user preferences and routes to channels.
4. Delivery attempts are tracked.
5. Failures are retried with exponential backoff.
