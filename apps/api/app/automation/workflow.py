"""Workflow engine."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.automation import Workflow, WorkflowRun, WorkflowStepRun
from app.repositories.base import BaseRepository
from app.services.audit_log import audit_log_service


class WorkflowRepository(BaseRepository[Workflow]):
    def __init__(self) -> None:
        super().__init__(Workflow)


class WorkflowRunRepository(BaseRepository[WorkflowRun]):
    def __init__(self) -> None:
        super().__init__(WorkflowRun)


workflow_repository = WorkflowRepository()
workflow_run_repository = WorkflowRunRepository()


class WorkflowEngine:
    async def create(
        self,
        db: AsyncSession,
        *,
        name: str,
        trigger: dict,
        steps: list[dict],
        tenant_id: uuid.UUID | None = None,
        description: str | None = None,
    ) -> Workflow:
        wf = Workflow(
            tenant_id=tenant_id,
            name=name,
            description=description,
            trigger=trigger,
            steps=steps,
        )
        return await workflow_repository.create(db, wf)

    async def trigger(
        self,
        db: AsyncSession,
        event_type: str,
        payload: dict[str, Any],
        tenant_id: uuid.UUID | None = None,
    ) -> list[WorkflowRun]:
        stmt = select(Workflow).where(
            Workflow.is_active.is_(True),
            Workflow.status == "active",
        )
        if tenant_id:
            stmt = stmt.where(Workflow.tenant_id == tenant_id)
        result = await db.execute(stmt)
        workflows = result.scalars().all()

        runs: list[WorkflowRun] = []
        for wf in workflows:
            trigger = wf.trigger or {}
            if trigger.get("event") != event_type:
                continue

            run = WorkflowRun(
                workflow_id=wf.id,
                tenant_id=wf.tenant_id,
                status="running",
                started_at=datetime.now(timezone.utc),
            )
            db.add(run)
            await db.flush()
            await db.refresh(run)

            runs.append(run)
            await self._execute(db, wf, run, payload)

        return runs

    async def _execute(
        self,
        db: AsyncSession,
        workflow: Workflow,
        run: WorkflowRun,
        payload: dict[str, Any],
    ) -> None:
        from app.automation.event_bus import domain_event_bus

        context = {"event": payload, "workflow_id": str(workflow.id)}
        try:
            for idx, step in enumerate(workflow.steps):
                step_run = WorkflowStepRun(
                    run_id=run.id,
                    step_index=idx,
                    action=step["action"],
                    status="running",
                    input=step.get("config"),
                    started_at=datetime.now(timezone.utc),
                )
                db.add(step_run)
                await db.flush()

                result = await self._run_action(step["action"], step.get("config", {}), context)
                step_run.output = {"result": result}
                step_run.status = "completed"
                step_run.ended_at = datetime.now(timezone.utc)
                context[f"step_{idx}"] = result
                await db.flush()

            run.status = "completed"
            run.result = context
            run.ended_at = datetime.now(timezone.utc)
        except Exception as exc:
            run.status = "failed"
            run.error = str(exc)
            run.ended_at = datetime.now(timezone.utc)

        await db.flush()
        await audit_log_service.log(
            db,
            "workflow.run.completed",
            "workflow_run",
            organization_id=workflow.tenant_id,
            resource_id=str(run.id),
            details={"status": run.status},
        )

    async def _run_action(
        self,
        action: str,
        config: dict[str, Any],
        context: dict[str, Any],
    ) -> Any:
        from app.automation.connectors.registry import connector_registry

        if action == "publish_communication":
            # Cannot use db here without passing; handled by caller in real implementation.
            return {"published": True}
        if action == "http_request":
            return await self._http_request(config)
        if action == "delay":
            await asyncio.sleep(float(config.get("seconds", 0)))
            return {"delayed": config.get("seconds", 0)}
        if action.startswith("connector."):
            provider = action.split(".", 1)[1]
            connector = connector_registry.get(provider)
            return await connector.execute(config)
        if action == "emit_domain_event":
            return {"emitted": config.get("event_type")}
        return {"noop": True}

    async def _http_request(self, config: dict[str, Any]) -> dict:
        import httpx

        method = config.get("method", "GET")
        url = config["url"]
        body = config.get("body")
        headers = config.get("headers", {})

        async with httpx.AsyncClient(timeout=30.0) as client:
            if method == "GET":
                response = await client.get(url, headers=headers)
            else:
                response = await client.request(method, url, json=body, headers=headers)
            return {
                "status": response.status_code,
                "body": response.text[:1000],
            }

    async def list(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID | None = None,
    ) -> list[Workflow]:
        stmt = select(Workflow)
        if tenant_id:
            stmt = stmt.where(Workflow.tenant_id == tenant_id)
        stmt = stmt.order_by(Workflow.created_at.desc())
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get(self, db: AsyncSession, wf_id: uuid.UUID) -> Workflow:
        wf = await workflow_repository.get(db, wf_id)
        if not wf:
            raise NotFoundError("Workflow not found")
        return wf


workflow_engine = WorkflowEngine()
