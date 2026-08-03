# Privacy-Conscious Analytics

## Architecture

- Use an event queue (Celery + Redis) to buffer analytics events.
- Send events to a privacy-friendly provider (Plausible, PostHog, or a self-hosted Clickhouse).
- Never collect PII without explicit consent.
- Hash or anonymize IP addresses.

## Tracked Events

- Page views.
- CTA clicks.
- Login and signup conversions.
- Feature discovery (accordion opens, tab switches).
- Core Web Vitals.

## Privacy

- Use `navigator.doNotTrack` and consent manager.
- Retain data for a fixed period (e.g., 90 days for events, 1 year for aggregates).
- Allow export and deletion of user data on request.
