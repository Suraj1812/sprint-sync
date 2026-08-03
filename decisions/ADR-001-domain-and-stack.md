# ADR-001: Domain and Technology Stack

## Status

Accepted

## Context

The request asked for an enterprise-grade web application with a random domain. A suitable domain must:

- Be modular enough to demonstrate Clean Architecture, feature-based frontend, and RBAC.
- Have a natural bounded-context split.
- Be commercially relevant for an enterprise SaaS.

## Decision

Select **agile project and sprint management** (SprintSync) as the domain.

Choose the following stack:

- Next.js 15 + React 19 + App Router for server-first rendering, streaming, and SEO.
- FastAPI + Python 3.13 for high-performance, typed, async backend.
- SQLAlchemy 2 + Alembic for relational persistence and migrations.
- PostgreSQL for ACID transactions and complex queries.
- Redis for cache, sessions, rate limits, and Celery broker.
- Celery for reliable background jobs.
- Pydantic v2 for end-to-end type safety.

## Consequences

- The frontend can leverage React Server Components for data fetching, minimizing client JavaScript.
- The backend can enforce RBAC at the service and repository layers.
- The domain (projects, sprints, tasks) maps cleanly to RESTful aggregate resources.
- Celery and Redis provide horizontal scalability for notifications and exports.
- PostgreSQL read replicas can be added for analytics and reporting.
