from __future__ import annotations

from datetime import datetime, timezone

from advanced_alchemy.extensions.fastapi import (
    base,
)
from advanced_alchemy.types import DateTimeUTC
from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import String

from python_web_service_boilerplate.common.common_function import get_login_user
from python_web_service_boilerplate.core.common_models import Deleted


class User(base.BigIntBase):
    __tablename__ = "user"

    username: Mapped[str] = mapped_column(
        String(length=64), index=True, unique=True, nullable=False, comment="The username"
    )
    password: Mapped[str] = mapped_column(String(length=512), nullable=False, comment="The password")
    email: Mapped[str] = mapped_column(String(length=256), index=True, nullable=False, comment="The email address")
    full_name: Mapped[str] = mapped_column(String(length=128), nullable=False, comment="The full name of the user")
    scopes: Mapped[str] = mapped_column(Text(), comment="The scopes/permissions assigned to the user, comma-separated")

    # Common audit fields
    created_by: Mapped[str] = mapped_column(
        String(length=64), default=get_login_user, nullable=False, comment="Created by"
    )
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), comment="Creation timestamp"
    )
    updated_by: Mapped[str | None] = mapped_column(String(64), default=get_login_user, comment="Last updated by")
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTimeUTC(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        comment="Last update timestamp",
    )
    deleted: Mapped[Deleted] = mapped_column(default=Deleted.N, comment="Deletion flag")
