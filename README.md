# SprintSync

A premium, enterprise-grade agile project management SaaS foundation.

[![CI](https://github.com/sprintsync/sprint-sync/actions/workflows/ci.yml/badge.svg)](https://github.com/sprintsync/sprint-sync/actions/workflows/ci.yml)
![License](https://img.shields.io/badge/license-Commercial-blue)

## Status

Production-ready foundation. All core architecture, security, testing, CI/CD, infrastructure, and documentation are in place. Business features are added in later phases.

## Stack

- **Frontend:** Next.js 15, React 19, TypeScript, Tailwind CSS, shadcn/ui, Radix UI, Framer Motion
- **Backend:** FastAPI, Python 3.13, SQLAlchemy 2, Alembic, Pydantic v2, Redis, Celery
- **Tooling:** pnpm, Turborepo, ESLint, Prettier, Husky, lint-staged, commitlint, Conventional Commits
- **Infrastructure:** Docker, Kubernetes, Docker Compose, PostgreSQL, Redis
- **Observability:** structlog, Prometheus, Grafana, OpenTelemetry, Sentry (integration guides)

## Quick start

```bash
# 1. Install Node 22, Python 3.13, pnpm, Docker.

# 2. Install dependencies and Python venv.
./scripts/setup.sh

# 3. Start backing services.
docker compose -f docker-compose.dev.yml up -d

# 4. Run the app stack.
./scripts/dev.sh
```

## Documentation

- [Getting started](docs/getting-started.md)
- [Environment setup](docs/environment-setup.md)
- [Architecture](docs/backend-architecture.md)
- [Security](docs/security-architecture.md)
- [Deployment](docs/deployment-guide.md)
- [CI/CD](docs/cicd-guide.md)
- [Monitoring](docs/monitoring-guide.md)
- [Testing](docs/testing-strategy.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Production readiness report](docs/production-readiness-report.md)
