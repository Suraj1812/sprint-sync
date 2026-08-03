# Incident Response Runbook

## Severity

- **SEV-1**: Full outage or data breach.
- **SEV-2**: Major feature down or security incident.
- **SEV-3**: Degraded performance or partial failure.
- **SEV-4**: Low-priority issue or question.

## Detection

- Alerting from Prometheus/Grafana.
- Sentry error spikes.
- Uptime monitoring from Pingdom or UptimeRobot.
- Customer reports.

## Response Steps

1. **Triage** — determine severity and impacted users.
2. **Assemble** — page on-call engineer(s).
3. **Mitigate** — roll back a bad release, scale pods, or disable a feature.
4. **Investigate** — use correlation IDs and logs to trace the issue.
5. **Resolve** — apply fix and verify.
6. **Post-Mortem** — within 24 hours for SEV-1/2.

## Rollback

```bash
# Roll back a Kubernetes deployment
kubectl rollout undo deployment/sprintsync-api -n sprintsync

# Revert Vercel
# Use Vercel dashboard to promote previous production deployment.

# Rotate compromised secret and redeploy
kubectl create secret generic sprintsync-api-secrets --from-env-file=.env.prod -n sprintsync
kubectl rollout restart deployment/sprintsync-api -n sprintsync
```
