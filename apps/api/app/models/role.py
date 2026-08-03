"""Role model for RBAC."""

from sqlalchemy import JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class Role(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "roles"
    __table_args__ = (UniqueConstraint("name"),)

    name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(255))
    permissions: Mapped[list[str]] = mapped_column(
        JSON,
        default=lambda: [],
        nullable=False,
    )

    users: Mapped[list["User"]] = relationship(  # type: ignore[name-defined]
        "User",
        back_populates="role",
    )
