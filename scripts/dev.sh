#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."

docker compose -f docker-compose.dev.yml up -d postgres redis

echo "==> Starting Next.js and FastAPI in watch mode"

pnpm --filter @sprint-sync/web dev &
(cd apps/api && source .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000) &

wait
