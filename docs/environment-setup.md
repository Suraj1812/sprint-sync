# Environment Setup

## Required variables

| Variable | Used by | Description |
| --- | --- | --- |
| `APP_NAME` | API | Application name for logs and OpenAPI. |
| `ENVIRONMENT` | API | `development` or `production`. |
| `DEBUG` | API | Enables SQL echo and debug logging. |
| `SECRET_KEY` | API | 256-bit secret for JWT signing. |
| `POSTGRES_USER` | Docker/Postgres | Database user. |
| `POSTGRES_PASSWORD` | Docker/Postgres | Database password. |
| `POSTGRES_DB` | Docker/Postgres | Database name. |
| `DATABASE_URL` | API | SQLAlchemy async URL. |
| `REDIS_URL` | API | Redis connection string. |
| `CORS_ORIGINS` | API | Comma-separated allowed origins. |
| `NEXT_PUBLIC_API_URL` | Web | Public API base URL. |

## File precedence

- `.env` — default values.
- `.env.local` — local overrides (gitignored).
- `.env.development` — committed dev defaults loaded by Next.js in `next dev`.
- `.env.production` — committed prod defaults loaded by Next.js in `next build`.

## Local setup

```bash
cp .env.example .env.local
# Edit .env.local with your values.
```
