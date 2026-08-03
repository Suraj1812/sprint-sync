"""Database seeding for foundational roles."""

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.role import Role


ADMIN_ROLES = [
    {
        "name": "user",
        "description": "Default user with workspace-level access.",
        "permissions": ["read", "write:own"],
    },
    {
        "name": "manager",
        "description": "Manager with team and project oversight.",
        "permissions": ["read", "write", "manage:team"],
    },
    {
        "name": "support",
        "description": "Support engineer with read and limited write access.",
        "permissions": ["read", "write:users:metadata", "read:audit"],
    },
    {
        "name": "operations",
        "description": "Operations with system and feature flag access.",
        "permissions": ["read", "write:flags", "write:settings", "read:audit"],
    },
    {
        "name": "billing",
        "description": "Billing manager with read and limited write access.",
        "permissions": ["read", "write:billing", "read:audit"],
    },
    {
        "name": "auditor",
        "description": "Read-only auditor with full visibility.",
        "permissions": ["read"],
    },
    {
        "name": "platform_admin",
        "description": "Platform administrator with broad system access.",
        "permissions": [
            "read",
            "write:users",
            "write:orgs",
            "write:flags",
            "write:settings",
            "read:audit",
        ],
    },
    {
        "name": "super_admin",
        "description": "Super administrator with full platform access.",
        "permissions": ["*"],
    },
]


async def seed_roles() -> None:
    async with AsyncSessionLocal() as session:
        existing = await session.execute(
            select(Role).where(Role.name.in_([r["name"] for r in ADMIN_ROLES]))
        )
        existing_names = {r.name for r in existing.scalars().all()}

        for role in ADMIN_ROLES:
            if role["name"] in existing_names:
                continue
            session.add(
                Role(
                    name=role["name"],
                    description=role["description"],
                    permissions=role["permissions"],
                )
            )

        await session.commit()
