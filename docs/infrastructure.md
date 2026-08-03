# Infrastructure Overview

## Kubernetes Manifests

The `k8s/` directory contains ready-to-apply manifests:

- `namespace.yaml` — `sprintsync` namespace.
- `configmap.yaml` — non-secret API configuration.
- `secrets.yaml` — secret references (replace with real values or a secrets operator).
- `postgres.yaml` — PostgreSQL `StatefulSet` with persistence.
- `redis.yaml` — Redis deployment.
- `api-deployment.yaml` — FastAPI deployment and service.
- `web-deployment.yaml` — Next.js deployment and service.
- `ingress.yaml` — NGINX ingress with TLS.
- `hpa.yaml` — Horizontal Pod Autoscaler for API and web.

## Resource Limits

Every container declares CPU/memory requests and limits to prevent noisy neighbors and enable the scheduler.

## Health Probes

- `livenessProbe` — restart if the container is stuck.
- `readinessProbe` — remove from service endpoints until ready.

## Scaling

HPA scales pods between `minReplicas` and `maxReplicas` based on CPU and memory utilization.

## Storage

Postgres uses a `PersistentVolumeClaim`. For production, use a managed database service instead of an in-cluster stateful set.
