# Final Release Checklist

## Development

- [ ] All features for the release are merged to `main`.
- [ ] Branch is green on CI.
- [ ] No `TODO`, `FIXME`, or placeholder comments remain in release code.

## Quality Assurance

- [ ] Unit tests pass (`pnpm test`, `pytest`).
- [ ] E2E tests pass (`pnpm test:e2e`).
- [ ] TypeScript and mypy have no errors.
- [ ] Lint and format checks pass.
- [ ] Coverage meets thresholds.

## Security

- [ ] No hardcoded secrets in the repository.
- [ ] `SECRET_KEY` is ≥ 32 characters and stored in a secret manager.
- [ ] `HSTS_ENABLED=true` and `ALLOWED_HOSTS` are configured in production.
- [ ] CSP headers are active and tested.
- [ ] Dependency audit passes.
- [ ] JWT and refresh token flows are validated.

## Performance

- [ ] Lighthouse Performance ≥ 95.
- [ ] Lighthouse SEO ≥ 100 (or as high as possible).
- [ ] Core Web Vitals pass on real devices.
- [ ] API p95 latency < 200 ms for authenticated endpoints.

## Accessibility

- [ ] WCAG AA manual review completed.
- [ ] Keyboard navigation works on all interactive elements.
- [ ] Color contrast passes.
- [ ] `prefers-reduced-motion` respected.

## SEO

- [ ] `robots.ts` and `sitemap.ts` deployed.
- [ ] Open Graph and Twitter metadata verified.
- [ ] Canonical URLs set.

## Infrastructure

- [ ] Docker images build and run as non-root.
- [ ] Kubernetes manifests reviewed.
- [ ] TLS and ingress configured.
- [ ] HPA and resource limits set.

## Deployment

- [ ] Staging deployment smoke tested.
- [ ] Database migrations tested in staging.
- [ ] Rollback plan documented.
- [ ] Canary or blue/green release configured.

## Monitoring

- [ ] Sentry DSN configured.
- [ ] Prometheus metrics scraped.
- [ ] Structured logs shipping.
- [ ] Alerting rules validated.

## Backups

- [ ] Database backups running.
- [ ] Restore procedure tested.
- [ ] RPO and RTO documented.

## Incident Response

- [ ] On-call rotation defined.
- [ ] Runbook reviewed with the team.
- [ ] Paging and escalation path confirmed.

## Documentation

- [ ] README updated.
- [ ] API docs accessible.
- [ ] Runbooks and guides current.

## Compliance

- [ ] Privacy policy and terms reviewed.
- [ ] Analytics and cookies reviewed for consent.

## Post-release verification

- [ ] Health checks pass.
- [ ] Login and registration work.
- [ ] Critical user journeys succeed.
- [ ] Error rate is near zero.
- [ ] Dashboards and alerts are healthy.
