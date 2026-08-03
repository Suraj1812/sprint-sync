# Workflow Architecture

## Overview

The workflow engine is a generic, event-driven rule engine. Workflows are stored as JSON `trigger` and `steps` and executed when matching domain events occur.

## Model

- `Workflow` — tenant-scoped, name, trigger, steps.
- `WorkflowRun` — execution instance.
- `WorkflowStepRun` — per-step result.

## Trigger Types

- `event` — matches `DomainEvent.event_type`.
- `schedule` — future support via Celery.
- `webhook` — incoming webhook received.
- `manual` — triggered by API.

## Actions

- `publish_communication` — notify via comms platform.
- `http_request` — call an external API.
- `delay` — pause execution.
- `connector.<provider>` — execute a third-party connector.
- `emit_domain_event` — publish another event.

## Engine Behavior

1. `domain_event_bus.publish` is called.
2. `WorkflowEngine.trigger` loads active workflows.
3. For each matching trigger, a `WorkflowRun` is created.
4. Steps execute sequentially and can reference previous step outputs via `context`.
5. Results and errors are persisted.

## Failure Handling

- Step failure sets run `status = failed` and stores `error`.
- Retry, timeouts, and parallel execution are future enhancements.
- Manual approval and conditionals are not yet implemented but the model supports them.
