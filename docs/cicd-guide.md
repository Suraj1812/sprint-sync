# CI/CD Guide

## Overview

The `CI` GitHub Actions workflow runs on every push and pull request to `main`. It is the quality gate before anything reaches production.

## Jobs

- `web-quality` — install, lint, typecheck, format check, build.
- `web-unit` — run Vitest unit and component tests.
- `api-quality` — Ruff, Ruff format check, mypy.
- `api-tests` — run `pytest` for backend tests.
- `e2e` — build and run Playwright end-to-end tests.
- `security` — dependency review, `pip-audit`, `npm audit`.
- `docker` — build container images after all other checks pass.

## Merge Requirements

All quality, test, security, and docker jobs must pass before merge. The `docker` job only runs on `main`.

## Local Validation

```bash
# Frontend
pnpm install
pnpm lint
pnpm typecheck
pnpm format:check
pnpm build
pnpm --filter @sprint-sync/web test

# Backend
cd apps/api
pip install -e ".[dev]"
ruff check .
ruff format . --check
mypy .
pytest
```
