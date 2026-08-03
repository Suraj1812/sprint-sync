# Backend Development

## Local Setup

1. Ensure PostgreSQL and Redis are running.
2. Copy `apps/api/.env.example` to `.env` and fill values.
3. Apply migrations: `alembic upgrade head`
4. Run the server:

```bash
cd apps/api
uvicorn app.main:app --reload
```

## Testing

```bash
pytest
```

## Background Workers

```bash
celery -A app.workers.celery_app worker -l info
```

## Logging

Logs are emitted as JSON by `structlog`. Each request is assigned a correlation ID returned in the `x-correlation-id` header. Pass `x-correlation-id` to trace requests through services.
