"""Automation, workflows, OAuth, API keys, and webhook API v1."""

import uuid
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin, get_current_user, get_db_session
from app.automation.api_key import api_key_service
from app.automation.event_bus import domain_event_bus
from app.automation.oauth import oauth_client_repository, oauth_service
from app.automation.webhook import webhook_service
from app.automation.workflow import workflow_engine
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.models.automation import (
    DomainEvent,
    WebhookSubscription,
    WorkflowRun,
)
from app.models.user import User
from app.schemas.automation import (
    ApiKeyCreate,
    ApiKeyCreateResponse,
    ApiKeyRead,
    DomainEventRead,
    OAuthAuthorizeRequest,
    OAuthClientCreate,
    OAuthClientCreateResponse,
    OAuthClientRead,
    OAuthTokenRequest,
    OAuthTokenResponse,
    WebhookSubscriptionCreate,
    WebhookSubscriptionRead,
    WorkflowCreate,
    WorkflowRead,
    WorkflowRunRead,
)
from app.schemas.common import APIResponse

automation_router = APIRouter(prefix="/automation", tags=["automation"])


@automation_router.post("/events/publish", response_model=DomainEventRead)
async def publish_domain_event(
    data: dict,
    db: AsyncSession = Depends(get_db_session),
    admin: User = Depends(get_current_admin),
) -> Any:
    event = await domain_event_bus.publish(
        db,
        data["event_type"],
        data.get("payload", {}),
        tenant_id=data.get("tenant_id"),
        correlation_id=data.get("correlation_id"),
        source=data.get("source"),
    )
    return event


@automation_router.get("/events", response_model=list[DomainEventRead])
async def list_events(
    status: str | None = None,
    db: AsyncSession = Depends(get_db_session),
    admin: User = Depends(get_current_admin),
) -> list[Any]:
    return await domain_event_bus.list_recent(db, status=status)


@automation_router.post("/workflows", response_model=WorkflowRead)
async def create_workflow(
    data: WorkflowCreate,
    db: AsyncSession = Depends(get_db_session),
    admin: User = Depends(get_current_admin),
) -> Any:
    return await workflow_engine.create(
        db,
        name=data.name,
        description=data.description,
        trigger=data.trigger,
        steps=data.steps,
        tenant_id=data.tenant_id,
    )


@automation_router.get("/workflows", response_model=list[WorkflowRead])
async def list_workflows(
    db: AsyncSession = Depends(get_db_session),
    admin: User = Depends(get_current_admin),
) -> list[Any]:
    return await workflow_engine.list(db)


@automation_router.get("/workflows/{wf_id}/runs", response_model=list[WorkflowRunRead])
async def list_workflow_runs(
    wf_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    admin: User = Depends(get_current_admin),
) -> list[Any]:
    stmt = select(WorkflowRun).where(WorkflowRun.workflow_id == wf_id).order_by(WorkflowRun.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@automation_router.post("/workflows/{wf_id}/trigger")
async def trigger_workflow(
    wf_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    admin: User = Depends(get_current_admin),
) -> APIResponse:
    wf = await workflow_engine.get(db, wf_id)
    run = WorkflowRun(workflow_id=wf.id, status="running")
    db.add(run)
    await db.flush()
    await db.refresh(run)
    await workflow_engine._execute(db, wf, run, {})
    return APIResponse(message="Triggered")


@automation_router.post("/webhooks", response_model=WebhookSubscriptionRead)
async def create_webhook(
    data: WebhookSubscriptionCreate,
    db: AsyncSession = Depends(get_db_session),
    admin: User = Depends(get_current_admin),
) -> Any:
    sub, _ = await webhook_service.create(
        db,
        name=data.name,
        url=data.url,
        events=data.events,
        tenant_id=data.tenant_id,
    )
    return sub


@automation_router.get("/webhooks", response_model=list[WebhookSubscriptionRead])
async def list_webhooks(
    db: AsyncSession = Depends(get_db_session),
    admin: User = Depends(get_current_admin),
) -> list[Any]:
    stmt = select(WebhookSubscription).order_by(WebhookSubscription.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@automation_router.get("/webhooks/{sub_id}/deliveries", response_model=list[Any])
async def list_webhook_deliveries(
    sub_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    admin: User = Depends(get_current_admin),
) -> list[Any]:
    return await webhook_service.list_deliveries(db, sub_id)


@automation_router.post("/api-keys", response_model=ApiKeyCreateResponse)
async def create_api_key(
    data: ApiKeyCreate,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> Any:
    key, raw = await api_key_service.create(
        db,
        user=user,
        name=data.name,
        scopes=data.scopes,
        expires_days=data.expires_days,
    )
    return {"id": key.id, "name": key.name, "key": raw, "key_preview": key.key_preview, "scopes": key.scopes}


@automation_router.get("/api-keys", response_model=list[ApiKeyRead])
async def list_api_keys(
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> list[Any]:
    return await api_key_service.list_for_user(db, user.id)


@automation_router.post("/api-keys/{key_id}/revoke")
async def revoke_api_key(
    key_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> Any:
    await api_key_service.revoke(db, key_id, user.id)
    return {"revoked": True}


@automation_router.post("/oauth/clients", response_model=OAuthClientCreateResponse)
async def create_oauth_client(
    data: OAuthClientCreate,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> Any:
    client, raw = await oauth_service.register_client(
        db,
        name=data.name,
        redirect_uris=data.redirect_uris,
        allowed_scopes=data.allowed_scopes,
        tenant_id=data.tenant_id,
    )
    return {
        "id": client.id,
        "tenant_id": client.tenant_id,
        "name": client.name,
        "client_id": client.client_id,
        "client_secret": raw,
        "redirect_uris": client.redirect_uris,
        "allowed_scopes": client.allowed_scopes,
        "is_active": client.is_active,
        "created_at": client.created_at,
    }


@automation_router.get("/oauth/clients", response_model=list[OAuthClientRead])
async def list_oauth_clients(
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> list[Any]:
    stmt = select(OAuthClient).order_by(OAuthClient.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@automation_router.post("/oauth/authorize")
async def authorize_oauth(
    data: OAuthAuthorizeRequest,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> dict:
    client = await oauth_client_repository.get_by_client_id(db, data.client_id)
    if not client or not client.is_active:
        raise AuthenticationError("Invalid client")
    if data.redirect_uri not in client.redirect_uris:
        raise AuthorizationError("Invalid redirect URI")

    code = await oauth_service.create_authorization_code(
        db,
        client,
        user,
        data.redirect_uri,
        data.scope,
        code_challenge=data.code_challenge,
    )
    return {
        "code": code,
        "state": data.state,
        "redirect_uri": data.redirect_uri,
    }


@automation_router.post("/oauth/token", response_model=OAuthTokenResponse)
async def token_oauth(
    data: OAuthTokenRequest,
    db: AsyncSession = Depends(get_db_session),
) -> Any:
    client = await oauth_client_repository.get_by_client_id(db, data.client_id)
    if not client or not client.is_active:
        raise AuthenticationError("Invalid client")
    # In a full implementation the client secret is verified against the hash.
    token, raw = await oauth_service.exchange_code(
        db,
        client,
        data.code,
        data.redirect_uri,
        code_verifier=data.code_verifier,
    )
    return OAuthTokenResponse(
        access_token=raw,
        token_type=token.token_type,
        expires_in=3600,
        refresh_token=token.refresh_token,
        scope=token.scope,
    )
