# Billing Platform Architecture

## Mission

A provider-agnostic, auditable, and extensible monetization layer that separates payments, pricing, subscriptions, entitlements, usage, invoicing, and financial reporting.

## Layers

```
app/billing/providers     → payment provider adapters (Stripe, Paddle, Razorpay)
app/billing/services      → business logic (customer, subscription, entitlement, usage, invoice, webhook, metrics)
app/api/v1/billing.py     → REST API
app/models/billing.py     → subscriptions, plans, prices, customers, invoices, payments, usage, events, entitlements
apps/web/app/admin/billing → admin dashboards
apps/web/app/billing      → customer billing portal
```

## Provider Abstraction

All providers implement `PaymentProvider` with `create_customer`, `create_checkout_session`, `create_portal_session`, `get_event`, and `verify_signature`. Switching providers is a one-line config change in `BILLING_PROVIDER`.

## Pricing Models

- **Free** via the `free` plan.
- **Recurring** with `month` or `year` billing interval.
- **One-time** with `one_time` interval.
- **Usage-based** with `usage_type` (seat, token, api_call, storage).
- **Trial** via `trial_days` on a price.
- **Enterprise** via `is_enterprise` and custom negotiation.

## Subscription Lifecycle

Created as `incomplete` during checkout, updated to `active` by webhooks. Supports cancel, change plan, pause/resume fields, and proration/renewal through provider events.

## Entitlements

Applications should call `EntitlementService.can_use` and `limit_for` instead of checking plan names. Free users get the `free` plan entitlements.

## Usage Tracking

`UsageRecord` captures metric, quantity, and timestamp. Aggregate usage is used for quota enforcement and billing.

## Webhook Security

- Signature verification per provider.
- Idempotency by `provider_event_id`.
- Retry counting and `processed` flags.
- Audit trail in `billing_events`.

## Analytics

`MetricsService` reports MRR, ARR, active subscriptions, and failed payments over 30 days.
