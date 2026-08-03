# Backend Architecture

## Overview

The SprintSync backend is a FastAPI application built around Clean Architecture principles. It is organized into clearly separated layers:

- `api/` — HTTP routing and dependencies.
- `core/` — configuration, logging, exceptions, and security.
- `db/` — database engine, sessions, base models, and seeding.
- `models/` — SQLAlchemy ORM entities.
- `schemas/` — Pydantic request, response, and validation models.
- `repositories/` — data access layer.
- `services/` — business logic orchestration.
- `middleware/` — cross-cutting concerns such as correlation IDs and request logging.
- `workers/` — Celery background task workers.
- `events/` — in-process domain event dispatcher.
- `tests/` — async test suite.

## Technology Decisions

- **FastAPI + Pydantic v2** — async-first, type-safe, OpenAPI generation.
- **SQLAlchemy 2.x + asyncpg** — async SQLAlchemy ORM with native Postgres support.
- **Alembic** — explicit, versioned schema migrations.
- **Redis** — caching, session/token coordination, and Celery broker.
- **Celery** — reliable background task queue for email, notifications, and jobs.
- **Argon2id** — modern, memory-hard password hashing.
- **python-jose** — JWT access and refresh tokens.
- **structlog** — structured, JSON-formatted logs with request correlation.
- **OpenTelemetry** — readiness hooks for tracing; instrumentation can be added without changing architecture.

## Flow

1. Request enters through FastAPI with `CorrelationIdMiddleware`.
2. Rate limiting and CORS are applied.
3. `get_db_session` dependency provides an async SQLAlchemy session.
4. `get_current_user` extracts and validates JWT tokens.
5. API layer calls a service, which calls repositories.
6. Application errors are raised as `AppError` subclasses and converted to consistent HTTP responses.
7. Background work is dispatched to Celery.
