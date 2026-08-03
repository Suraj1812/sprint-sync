"""OAuth 2.0 application service."""

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError
from app.models.automation import (
    OAuthAuthorizationCode,
    OAuthClient,
    OAuthToken,
)
from app.models.user import User
from app.repositories.base import BaseRepository


class OAuthClientRepository(BaseRepository[OAuthClient]):
    def __init__(self) -> None:
        super().__init__(OAuthClient)

    async def get_by_client_id(
        self,
        db: AsyncSession,
        client_id: str,
    ) -> OAuthClient | None:
        stmt = select(OAuthClient).where(OAuthClient.client_id == client_id).limit(1)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()


oauth_client_repository = OAuthClientRepository()


class OAuthService:
    def _hash(self, value: str) -> str:
        return hashlib.sha256(value.encode()).hexdigest()

    async def register_client(
        self,
        db: AsyncSession,
        *,
        name: str,
        redirect_uris: list[str],
        allowed_scopes: list[str],
        tenant_id: uuid.UUID | None = None,
    ) -> tuple[OAuthClient, str]:
        client_id = "cli_" + secrets.token_urlsafe(16)
        raw_secret = "cs_" + secrets.token_urlsafe(32)
        client = OAuthClient(
            tenant_id=tenant_id,
            name=name,
            client_id=client_id,
            client_secret_hash=self._hash(raw_secret),
            redirect_uris=redirect_uris,
            allowed_scopes=allowed_scopes,
        )
        await oauth_client_repository.create(db, client)
        return client, raw_secret

    async def create_authorization_code(
        self,
        db: AsyncSession,
        client: OAuthClient,
        user: User,
        redirect_uri: str,
        scope: str,
        *,
        code_challenge: str | None = None,
    ) -> str:
        code = secrets.token_urlsafe(32)
        auth_code = OAuthAuthorizationCode(
            code=code,
            client_id=client.client_id,
            user_id=user.id,
            redirect_uri=redirect_uri,
            scope=scope,
            code_challenge=code_challenge,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        )
        db.add(auth_code)
        await db.flush()
        return code

    async def exchange_code(
        self,
        db: AsyncSession,
        client: OAuthClient,
        code: str,
        redirect_uri: str,
        *,
        code_verifier: str | None = None,
    ) -> tuple[OAuthToken, str]:
        stmt = (
            select(OAuthAuthorizationCode)
            .where(
                OAuthAuthorizationCode.code == code,
                OAuthAuthorizationCode.client_id == client.client_id,
            )
            .limit(1)
        )
        result = await db.execute(stmt)
        auth_code = result.scalar_one_or_none()

        if not auth_code or auth_code.used_at:
            raise AuthenticationError("Invalid authorization code")
        if auth_code.expires_at < datetime.now(timezone.utc):
            raise AuthenticationError("Authorization code expired")
        if auth_code.redirect_uri and auth_code.redirect_uri != redirect_uri:
            raise AuthenticationError("Redirect URI mismatch")

        auth_code.used_at = datetime.now(timezone.utc)

        token = "tok_" + secrets.token_urlsafe(32)
        refresh = "ref_" + secrets.token_urlsafe(32)
        oauth_token = OAuthToken(
            token=token,
            refresh_token=refresh,
            client_id=client.client_id,
            user_id=auth_code.user_id,
            scope=auth_code.scope,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        db.add(oauth_token)
        await db.flush()
        return oauth_token, token

    async def introspect(
        self,
        db: AsyncSession,
        token: str,
    ) -> OAuthToken | None:
        stmt = (
            select(OAuthToken)
            .where(
                OAuthToken.token == token,
                OAuthToken.revoked_at.is_(None),
            )
            .limit(1)
        )
        result = await db.execute(stmt)
        t = result.scalar_one_or_none()
        if not t or (t.expires_at and t.expires_at < datetime.now(timezone.utc)):
            return None
        return t

    async def revoke_token(
        self,
        db: AsyncSession,
        token: str,
    ) -> None:
        stmt = select(OAuthToken).where(OAuthToken.token == token).limit(1)
        result = await db.execute(stmt)
        t = result.scalar_one_or_none()
        if t:
            t.revoked_at = datetime.now(timezone.utc)
            await db.flush()


oauth_service = OAuthService()
