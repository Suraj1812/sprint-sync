# Admin Billing

## Dashboard

- `GET /api/v1/billing/admin/metrics` — MRR, ARR, active subscriptions, failed payments.
- `/admin/billing` — revenue overview.

## Operations

- `/admin/billing/subscriptions` — view all subscriptions.
- `/admin/billing/invoices` — invoice lookup and refund reference.
- `/admin/billing/events` — webhook event log and retry status.

## Manual Adjustments

For refunds or credits, create `Invoice` or `Payment` records with an admin note in `metadata`. All changes are audit logged via `BillingEvent` and the existing `AuditLog` service.

## Future Work

- Tax calculation for VAT/GST based on `billing_address`.
- Credit notes and proration ledger.
- Dunning management for failed payments.
- Customer LTV and churn cohort dashboards.
