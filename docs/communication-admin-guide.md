# Communication Admin Guide

## Dashboards

- **Communications overview** — total, pending, completed, failed events by channel.
- **Email templates** — list, create, preview.

## Endpoints

- `GET /api/v1/communications/admin/templates`
- `POST /api/v1/communications/admin/templates`
- `POST /api/v1/communications/admin/templates/preview`
- `POST /api/v1/communications/admin/send-email`
- `GET /api/v1/communications/admin/stats`

## Monitoring

Track:
- Delivery success rate
- Queue depth (`pending` count)
- Retry rate (`failed` count)
- Provider health

## Operations

- Switch providers by changing `EMAIL_PROVIDER`.
- Pause a template by setting `is_active = False`.
- Re-send events by calling `dispatch` again after fixing the issue.
