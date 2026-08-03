# Monitoring Guide

## Observability Stack

- **Logs**: `structlog` JSON logs shipped to a log aggregator (Datadog, Cloud Logging, ELK).
- **Metrics**: Prometheus endpoint + Grafana dashboards.
- **Traces**: OpenTelemetry for request correlation across services.
- **Errors**: Sentry for frontend and backend exception tracking.

## Key Metrics

- Core Web Vitals (LCP, INP, CLS).
- API request latency (p50, p95, p99).
- API error rate and throughput.
- Database query duration.
- Redis cache hit rate.
- Pod CPU, memory, and restart count.

## Correlation IDs

Every request receives an `x-correlation-id`. This ID is propagated through:

- Next.js middleware.
- FastAPI `CorrelationIdMiddleware`.
- `structlog` context variables.
- HTTP headers to downstream services.

## Dashboards

Recommended Grafana dashboards:

1. API Health: RPS, latency, error rate.
2. Frontend: Core Web Vitals, page load times.
3. Infrastructure: pod resource usage, HPA scaling.
4. Security: login failures, rate-limit hits, permission denials.
