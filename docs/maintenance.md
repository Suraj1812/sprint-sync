# Maintenance Guide

## Regular tasks

### Weekly

- Review CI/CD failure rates.
- Scan dependency vulnerabilities (`pnpm audit`, `pip-audit`).
- Review error logs and Sentry issues.
- Verify backup completion.

### Monthly

- Rotate non-production secrets.
- Review user access and RBAC assignments.
- Update patch-level dependencies.
- Run performance and accessibility checks.

### Quarterly

- Rotate production secrets and TLS certificates.
- Penetration test or security review.
- Capacity planning and cost review.
- Review and update documentation.

## Dependency updates

- Use `pnpm update` and `pip` patch updates.
- Run the full test suite before promoting.
- For major versions, plan a deprecation window.

## Database

- Keep Alembic migrations sequential.
- Test migrations against a copy of production data before release.
- Never edit existing migration files that have been applied to production.

## Backups

- Daily full PostgreSQL backups with 30-day retention.
- Hourly point-in-time recovery logs.
- Quarterly restore drills.
