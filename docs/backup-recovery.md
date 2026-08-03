# Backup and Recovery

## Database Backups

- **Schedule**: continuous WAL + daily full backups.
- **Retention**: 30 days of daily backups, 7 days of hourly PITR.
- **Encryption**: backups encrypted at rest.
- **Offsite**: store in S3-compatible object storage in a different region.

## Restore Procedure

1. Identify the target recovery point.
2. Provision a new managed database instance.
3. Restore from the latest full backup.
4. Replay WAL to the desired point.
5. Update `DATABASE_URL` and restart API pods.
6. Verify with health checks and smoke tests.

## Disaster Recovery Objectives

- **RPO**: 1 hour.
- **RTO**: 4 hours.

## High Availability

- Use managed PostgreSQL with replicas.
- Run Redis in a replicated or managed configuration.
- Deploy API pods across multiple availability zones.
