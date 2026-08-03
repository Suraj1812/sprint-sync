# Webhook Guide

## Security

- `WebhookService.receive` verifies the provider signature using the configured secret.
- Invalid signatures return a `400` response; the provider will retry.
- Only `v1` signatures are accepted for Stripe.

## Idempotency

Each event is stored in `billing_events` keyed by `(provider, provider_event_id)`. Duplicate processed events are ignored.

## Processing

Supported Stripe events:
- `checkout.session.completed` → activate subscription.
- `invoice.payment_succeeded` → create invoice record.
- `invoice.payment_failed` / `payment_intent.payment_failed` → record failed payment.
- `customer.subscription.deleted` → mark subscription canceled.
- `customer.subscription.updated` → sync subscription status.

## Dead Letter Queue

Failed events are stored with `error` and `attempts`. A background worker can retry `BillingEvent` rows where `processed = false` and `retry_at` has passed.
