# Release Process

1. **Feature Branch**: open a PR, CI must pass.
2. **Code Review**: approve with security and ops review.
3. **Merge to `main`**: deploys to staging automatically.
4. **Smoke Tests**: run staging health checks and e2e suite.
5. **Tag Release**: `git tag -a v1.x.x -m "Release ..."`.
6. **Production Deploy**: promote staging image to production.
7. **Monitor**: watch error rate, latency, and logs for 30 minutes.
8. **Announce**: update status page and notify stakeholders.

## Versioning

Use semantic versioning (MAJOR.MINOR.PATCH).

## Hotfixes

- Branch from `main`, fix, open PR, merge, and immediately tag.
- Cloud Run and Vercel support near-instant redeployment.
