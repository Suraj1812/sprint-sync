# Webhook Guide

## Outgoing Webhooks

`WebhookSubscription` defines a URL and list of `events` to receive. Deliveries are signed with HMAC-SHA256 using the subscription `secret`.

## Signature

Receivers should verify the `X-Webhook-Signature` header:

```python
hmac.new(secret.encode(), body, hashlib.sha256).hexdigest() == signature
```

## Delivery Logs

`WebhookDelivery` records status, response status, response body, and error. Subscriptions are disabled after 5 consecutive failures.

## Retry

Retry is not yet automatic. Failures can be replayed by re-publishing the `DomainEvent` or calling the delivery endpoint.

## Incoming Webhooks

The architecture supports incoming webhooks as workflow triggers. Register a `workflow` with `trigger: {"type": "webhook"}` and an endpoint that creates a `DomainEvent`.
