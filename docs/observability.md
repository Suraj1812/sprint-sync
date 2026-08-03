# Observability

## Metrics

Track:
- Workflow run counts and status
- Step duration
- Domain event processing time
- Webhook delivery success/failure
- API key usage
- OAuth token issuance and revocation
- Connector latency

## Data Sources

- `workflow_runs` and `workflow_step_runs` for workflow observability.
- `domain_events` for event bus health.
- `webhook_deliveries` for webhook reliability.
- `api_keys.usage_count` and `last_used_at`.
- `audit_logs` for security and compliance.

## Alerts

Future alerts:
- High failed webhook ratio
- Growing `pending` domain event queue
- API key with unusual usage
- OAuth token abuse

## Dashboards

Admin dashboards are at `/admin/automation` for workflows, `/admin/communications` for delivery, and `/admin/system` for logs.
