# Deployment Guide

## Target Environments

| Environment | Purpose | Trigger |
|-------------|---------|---------|
| Development | Local + feature branches | Manual |
| Staging | Integration + QA | Merge to `main` |
| Production | Customer traffic | Tagged release |

## Frontend — Vercel

The Next.js frontend is ideal for Vercel:

1. Connect the GitHub repository to Vercel.
2. Set framework preset to Next.js 15.
3. Configure environment variables:
   - `NEXT_PUBLIC_API_URL=https://api.sprintsync.dev`
4. Vercel builds and deploys on every push.
5. Preview deployments are generated for every pull request.

## Backend — Cloud Run (recommended)

Cloud Run is the preferred backend platform:

- **Serverless** scaling with request-based billing.
- **Built-in HTTPS** and load balancing.
- **Blue/green and canary** with traffic splitting.
- **Managed secrets** integration.

### Steps

1. Build and push the image: `docker build -f docker/Dockerfile.api -t gcr.io/...`
2. Deploy to Cloud Run with `gcloud run deploy`.
3. Set environment variables and secrets.
4. Run `alembic upgrade head` from a Cloud Run job or Cloud Build step.

## Database

Use a managed PostgreSQL (Cloud SQL) with automated backups. Connect via private IP or Cloud SQL Auth Proxy.

## Cache

Use managed Redis (Cloud Memorystore) for sessions, refresh tokens, and Celery.

## CDN

Cloudflare in front of Vercel for asset caching, DDoS protection, and extra security headers.
