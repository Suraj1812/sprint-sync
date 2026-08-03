# Folder Structure Guide

## `apps/`

### `apps/web`
- `app/` — Next.js 15 App Router routes, layouts, error boundaries, loading UI, and 404.
- `lib/` — Typed utilities such as `api.ts` for server-side fetch wrappers and `env.ts` for runtime env validation.
- `package.json` — Scoped as `@sprint-sync/web`. Depends on shared packages and Next.js ecosystem.

### `apps/api`
- `app/core/` — Application-agnostic services: config, security, logging, exceptions.
- `app/db/` — SQLAlchemy base, async session, Redis client.
- `app/api/` — FastAPI routers and dependency wiring. `v1` holds versioned routers.
- `alembic/` — Migration configuration, `env.py`, `script.py.mako`, and `versions/`.
- `pyproject.toml` — PEP 621 project metadata and dependencies.

## `packages/`

### `packages/config`
Shared ESLint, Prettier, TypeScript, and Tailwind configuration. Exposed through `package.json` `exports` so apps can extend them without duplication.

### `packages/types`
TypeScript types that are shared between the front end and the back end (e.g., error shapes, API response contracts).

### `packages/utils`
Framework-agnostic helpers. Currently contains `cn` for `clsx` + `tailwind-merge`.

### `packages/validation`
Zod schemas. `env.ts` validates `NEXT_PUBLIC_*` variables on the client.

### `packages/ui`
Headless, accessible components built on Radix UI. Depends on `@sprint-sync/utils` for styling.

## `archive/`

`archive/phase2-identity/` preserves the Phase 2 Identity & Access feature code as a reference while the foundation remains clean of business logic.
