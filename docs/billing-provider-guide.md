# Payment Provider Integration

## Supported Providers

- **Stripe** (`stripe`) — primary. Implements customer, checkout, portal, webhook signature.
- **Paddle** (`paddle`) — placeholder.
- **Razorpay** (`razorpay`) — placeholder for India.

## Adding a Provider

1. Create `app/billing/providers/<name>.py`.
2. Subclass `PaymentProvider` and implement all methods.
3. Register in `app/billing/providers/registry.py`.
4. Add environment variables to `app/core/config.py` and `.env.example`.

## Configuration

```bash
BILLING_PROVIDER=stripe
STRIPE_SECRET_KEY=sk_...
STRIPE_PUBLISHABLE_KEY=pk_...
STRIPE_WEBHOOK_SECRET=whsec_...
PADDLE_API_KEY=...
RAZORPAY_KEY_ID=...
RAZORPAY_KEY_SECRET=...
```

## Webhook Endpoints

- `POST /api/v1/billing/webhooks/stripe`
- `POST /api/v1/billing/webhooks/paddle`
- `POST /api/v1/billing/webhooks/razorpay`

Each endpoint reads its provider-specific signature header.
