# SprintSync Architecture

## Overview

SprintSync is a cloud-native, full-stack SaaS built as a pnpm + Turborepo monorepo. The architecture separates deployable applications (`apps/*`) from shared packages (`packages/*`) to eliminate duplication and enforce a single source of truth for configuration, types, validation, and UI primitives.

## High-level design

```
[Client]
  -> CDN / Edge
    -> apps/web (Next.js App Router, React Server Components)
      -> apps/api (FastAPI, async SQLAlchemy 2)
        -> PostgreSQL (primary data)
        -> Redis (cache, sessions, queues)
        -> Celery workers (background tasks)
```

## Apps

- `apps/web` — Next.js 15 with the App Router. Server Components fetch data; client components are used only for interactivity. Uses `next-themes` for dark/light mode and `@sprint-sync/ui` for shared components.
- `apps/api` — FastAPI with Clean Architecture. Dependency injection is performed through FastAPI `Depends`. Database access is through `AsyncSession`. Alembic manages migrations.

## Shared packages

- `@sprint-sync/config` — One source for `tsconfig`, `eslint`, `prettier`, and `tailwind` configuration.
- `@sprint-sync/types` — Shared TypeScript interfaces and API contract shapes.
- `@sprint-sync/utils` — Framework-agnostic utilities (`cn`, formatting).
- `@sprint-sync/validation` — Zod schemas used on both the client (form validation) and the server (request validation reference).
- `@sprint-sync/ui` — Headless, accessible, Radix-based components styled with Tailwind.

## Security and quality

- Environment variables are validated at runtime. Secrets never live in source control.
- Authentication and authorization use short-lived JWTs and rotated, hashed refresh tokens stored in Redis.
- Pre-commit hooks run linting, formatting, type checking, and commit message validation.
- CI builds and tests both the web and API applications.

## Deployment

Multi-stage Dockerfiles produce minimal images. `docker-compose.dev.yml` runs Postgres, Redis, and Mailhog locally. `docker-compose.yml` runs the production stack.
