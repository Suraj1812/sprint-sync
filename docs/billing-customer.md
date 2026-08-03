# Customer Billing Portal

## Endpoints

- `GET /api/v1/billing/plans` — list available plans.
- `GET /api/v1/billing/customer` — get or create customer.
- `POST /api/v1/billing/checkout` — create checkout session and redirect to provider.
- `POST /api/v1/billing/portal` — open customer portal.
- `GET /api/v1/billing/subscriptions` — list subscriptions.
- `POST /api/v1/billing/subscriptions/{id}/cancel` — cancel.
- `POST /api/v1/billing/subscriptions/{id}/change` — change plan.
- `GET /api/v1/billing/invoices` — invoice history.
- `GET /api/v1/billing/entitlements` — current entitlements.
- `POST /api/v1/billing/usage` — record usage (internal).

## Usage

`/api/v1/billing/usage` records metered events. Combine with `GET /api/v1/billing/entitlements` to enforce quota before running AI or storage operations.
