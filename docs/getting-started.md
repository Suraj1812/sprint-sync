# Getting Started

## Prerequisites

- Node.js 22 (see `.nvmrc`)
- Python 3.13 (see `.python-version`)
- pnpm 9.15.0
- Docker and Docker Compose

## Installation

```bash
./scripts/setup.sh
```

This installs pnpm workspace dependencies and creates the Python virtual environment in `apps/api/.venv`.

## Running the development stack

```bash
# Start Postgres, Redis, and Mailhog.
docker compose -f docker-compose.dev.yml up -d

# Start web and API in watch mode.
./scripts/dev.sh
```

The web app runs on `http://localhost:3000` and the API on `http://localhost:8000`.

## Database migrations

```bash
cd apps/api
source .venv/bin/activate
alembic revision --autogenerate -m "init"
alembic upgrade head
```
