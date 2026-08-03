# Development Guide

## Workflow

1. Create a feature branch from `main`.
2. Make changes in the relevant `app/` or `package/`.
3. Run `pnpm lint`, `pnpm typecheck`, and `pnpm test` before committing.
4. Write Conventional Commit messages.
5. Open a PR using the pull request template.

## Linting and formatting

- **TypeScript/TSX:** ESLint + Prettier
- **Python:** Ruff (lint + format) + mypy (type check)
- **Pre-commit hooks:** Husky runs `lint-staged` for staged files and `commitlint` for the commit message.

## Environment variables

Never commit secrets. Use `.env.local` for local overrides. See `.env.example` for all required variables.

## Adding a feature

1. Add domain models, repositories, and services in `apps/api/app/...`.
2. Add Zod schemas in `packages/validation` if shared between front end and back end.
3. Add pages, components, and actions in `apps/web/app/...`.
4. Add or update Alembic migrations when changing SQLAlchemy models.
