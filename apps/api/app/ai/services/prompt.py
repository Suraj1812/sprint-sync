"""Prompt management service."""

import uuid
from string import Template
from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.prompt import Prompt, PromptVersion
from app.repositories.base import BaseRepository


class PromptRepository(BaseRepository[Prompt]):
    def __init__(self) -> None:
        super().__init__(Prompt)

    async def get_by_name(self, db: AsyncSession, name: str) -> Prompt | None:
        stmt = select(Prompt).where(Prompt.name == name)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()


class PromptVersionRepository(BaseRepository[PromptVersion]):
    def __init__(self) -> None:
        super().__init__(PromptVersion)

    async def latest(
        self,
        db: AsyncSession,
        prompt_id: uuid.UUID,
    ) -> PromptVersion | None:
        stmt = (
            select(PromptVersion)
            .where(PromptVersion.prompt_id == prompt_id)
            .order_by(desc(PromptVersion.version))
            .limit(1)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()


prompt_repository = PromptRepository()
prompt_version_repository = PromptVersionRepository()


class PromptService:
    async def get_or_create(
        self,
        db: AsyncSession,
        name: str,
        user_template: str,
        system: str | None = None,
        description: str | None = None,
        variables: list[str] | None = None,
    ) -> Prompt:
        prompt = await prompt_repository.get_by_name(db, name)
        if prompt:
            return prompt

        prompt = Prompt(
            name=name,
            description=description,
            variables=variables or [],
        )
        prompt = await prompt_repository.create(db, prompt)
        version = PromptVersion(
            prompt_id=prompt.id,
            version=1,
            system=system,
            user_template=user_template,
        )
        version = await prompt_version_repository.create(db, version)
        prompt.default_version_id = version.id
        await db.flush()
        return prompt

    async def render(
        self,
        db: AsyncSession,
        name: str,
        variables: dict[str, Any] | None = None,
        version: int | None = None,
    ) -> tuple[str | None, str]:
        prompt = await prompt_repository.get_by_name(db, name)
        if not prompt:
            raise NotFoundError(f"Prompt not found: {name}")

        if version:
            stmt = select(PromptVersion).where(
                PromptVersion.prompt_id == prompt.id,
                PromptVersion.version == version,
            )
            result = await db.execute(stmt)
            pv = result.scalar_one_or_none()
        else:
            if prompt.default_version_id is None:
                pv = await prompt_version_repository.latest(db, prompt.id)
            else:
                pv = await prompt_version_repository.get(db, prompt.default_version_id)

        if not pv:
            raise NotFoundError("Prompt version not found")

        variables = variables or {}
        rendered = Template(pv.user_template).safe_substitute(variables)
        return pv.system, rendered

    async def create_version(
        self,
        db: AsyncSession,
        prompt_id: uuid.UUID,
        system: str | None,
        user_template: str,
        metadata: dict | None = None,
    ) -> PromptVersion:
        latest = await prompt_version_repository.latest(db, prompt_id)
        next_version = (latest.version + 1) if latest else 1
        version = PromptVersion(
            prompt_id=prompt_id,
            version=next_version,
            system=system,
            user_template=user_template,
            metadata=metadata,
        )
        return await prompt_version_repository.create(db, version)

    async def set_default_version(
        self,
        db: AsyncSession,
        prompt: Prompt,
        version_id: uuid.UUID,
    ) -> Prompt:
        prompt.default_version_id = version_id
        await db.flush()
        return prompt


prompt_service = PromptService()
