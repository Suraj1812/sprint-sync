# Feature Flag Guide

## Model

- `key` — unique per environment.
- `name` — human-readable label.
- `environment` — `production` by default.
- `enabled` — master toggle.
- `rollout_percentage` — 0–100.
- `targeting` — JSON object for user/role/org-specific rules.
- `scheduled_at` — optional future activation time.

## Usage

Create a flag in the admin UI or via `POST /api/v1/admin/feature-flags`. Toggle it, adjust rollout, and audit changes automatically.

## Client Integration

The public API will expose a `/flags` endpoint in a later phase. For now, flags are managed by operations staff through the admin UI.
