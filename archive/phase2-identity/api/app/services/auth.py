from uuid import UUID

from app.core.exceptions import AuthenticationError, ConflictError
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.repositories.user import IUserRepository
from app.schemas.auth import TokenPair
from app.services.token import TokenService


class AuthService:
    def __init__(
        self,
        user_repo: IUserRepository,
        token_service: TokenService,
    ) -> None:
        self._user_repo = user_repo
        self._token_service = token_service

    async def register(
        self,
        email: str,
        password: str,
        full_name: str | None = None,
        role: str = "member",
    ) -> TokenPair:
        existing = await self._user_repo.get_by_email(email)
        if existing:
            raise ConflictError("Email already registered")
        hashed = hash_password(password)
        user = await self._user_repo.create(email, hashed, full_name, role)
        return await self._issue_token_pair(str(user.id), user.role)

    async def login(self, email: str, password: str) -> TokenPair:
        user = await self._user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid credentials")
        return await self._issue_token_pair(str(user.id), user.role)

    async def refresh(self, token: str) -> TokenPair:
        user_id = await self._token_service.consume_refresh_token(token)
        if not user_id:
            raise AuthenticationError("Invalid or expired refresh token")
        user = await self._user_repo.get_by_id(UUID(user_id))
        if not user or not user.is_active:
            raise AuthenticationError("User not found or inactive")
        return await self._issue_token_pair(str(user.id), user.role)

    async def logout(self, token: str | None) -> None:
        if token:
            await self._token_service.revoke_refresh_token(token)

    async def _issue_token_pair(self, user_id: str, role: str) -> TokenPair:
        access = create_access_token(user_id, role)
        refresh = await self._token_service.create_refresh_token(user_id)
        return TokenPair(
            access_token=access,
            refresh_token=refresh,
            user_id=UUID(user_id),
        )
