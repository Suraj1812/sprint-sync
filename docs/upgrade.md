# Upgrade Guide

## Framework upgrades

### Next.js / React

1. Read the release notes and breaking changes.
2. Update `package.json` versions.
3. Run `pnpm install`.
4. Run `pnpm typecheck` and fix TypeScript issues.
5. Run `pnpm build` and `pnpm test`.
6. Deploy to staging and run Playwright e2e tests.

### FastAPI / Python

1. Update `apps/api/pyproject.toml`.
2. Recreate the virtual environment.
3. Run `ruff check`, `mypy`, `pytest`.
4. Test in Docker before promoting.

## Database migrations

1. Generate migration: `alembic -c apps/api/alembic.ini revision --autogenerate -m "..."`
2. Review the generated migration.
3. Test locally against a production-like dataset.
4. Apply to staging first, then production after smoke tests.

## Rollback

- For deployment: use previous Docker image or Vercel deployment.
- For database: restore from backup or reverse the migration if safe.
