# Coding Standards

## TypeScript

- Strict mode is enabled. No `any` without an explicit, documented exception.
- Prefer `interface` for object shapes and `type` for unions.
- Use absolute imports or workspace package imports; avoid deep relative paths.
- Server Components are the default; mark client components with `"use client"`.
- Error boundaries, loading UI, and `not-found.tsx` must exist for every route group.

## Python

- Use `async`/`await` for I/O and SQLAlchemy `AsyncSession`.
- Follow the Repository Pattern and the Service Layer. Business logic lives in services.
- Use Pydantic v2 for request/response schemas and settings.
- Use `UUID` primary keys and prefer schemas per bounded context in Postgres.

## Shared packages

- Never duplicate code between `apps/web` and `apps/api`.
- `packages/config` is the only source for tooling configuration.
- `packages/validation` is the only source for shared Zod schemas.
