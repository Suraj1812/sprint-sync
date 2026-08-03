# Communication Queue and Retry Guide

## Events

`CommunicationEvent` is the queue. Each event has `status`, `retry_count`, `next_retry`, and `processed_at`.

## Dispatch

`EventBusService.dispatch`:
- Sets `status = processing`
- Iterates over handlers for the event type
- Skips disabled channels
- Records delivery attempts
- On failure, sets `status = failed` and computes `next_retry` as `now + 2^retry_count minutes`
- On success, sets `status = completed`

## Retry

`EventBusService.retry_failed` fetches events with `status = failed`, `next_retry <= now`, and `retry_count < 10`, and dispatches them again.

## Background Workers

Use Celery or a scheduled job to call `event_bus.retry_failed(db)` periodically.
