# Troubleshooting Guide

## Local development

### `pnpm install` fails

- Ensure pnpm >= 9.15.0: `pnpm --version`
- Delete `node_modules` and `.pnpm-store`, then `pnpm install --frozen-lockfile`

### Backend cannot connect to database

- Check PostgreSQL is running: `docker compose -f docker-compose.dev.yml ps`
- Verify `DATABASE_URL` in `apps/api/.env`
- Run migrations: `alembic -c apps/api/alembic.ini upgrade head`

### Redis errors

- Check Redis container: `docker compose -f docker-compose.dev.yml logs redis`
- Ensure `REDIS_URL` matches the running instance

### Tests fail

- Frontend: `pnpm --filter @sprint-sync/web test`
- Backend: `cd apps/api && pytest`
- E2E: `pnpm --filter @sprint-sync/web build && pnpm --filter @sprint-sync/web test:e2e`

## Production

### Pods not ready

- Check events: `kubectl get events -n sprintsync`
- Check logs: `kubectl logs -n sprintsync deployment/sprintsync-api`

### High latency

- Inspect API p95/p99 in Grafana
- Check Redis cache hit rate
- Review slow database queries in PostgreSQL logs

### Security incident

- Rotate `SECRET_KEY` immediately
- Revoke refresh tokens: `redis-cli --scan --pattern "refresh_token:*" | xargs redis-cli del`
- Follow [incident response notes](incident-response.md)
