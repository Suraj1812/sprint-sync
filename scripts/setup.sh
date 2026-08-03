#!/usr/bin/env bash
set -e

echo "==> SprintSync setup"

cd "$(dirname "$0")/.."

if ! command -v pnpm &>/dev/null; then
  echo "pnpm is required. Install with: corepack prepare pnpm@9.15.0 --activate"
  exit 1
fi

pnpm install

cd apps/api
if ! command -v uv &>/dev/null; then
  python3.13 -m venv .venv
  source .venv/bin/activate
  pip install -e ".[dev]"
else
  uv venv -p 3.13 .venv
  source .venv/bin/activate
  uv pip install -e ".[dev]"
fi

echo "==> Setup complete. Copy .env.example to .env.local and start services."
