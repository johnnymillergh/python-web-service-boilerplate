from __future__ import annotations

from datetime import datetime

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

    username: Mapped[str] = mapped_column(String(length=64), index=True, unique=True, comment="The username")
    password: Mapped[str] = mapped_column(String(length=512), comment="The password")
    email: Mapped[str] = mapped_column(String(length=256), index=True, comment="The email address")
    full_name: Mapped[str] = mapped_column(String(length=128), comment="The full name of the user")
    scopes: Mapped[str] = mapped_column(Text(), comment="The scopes/permissions assigned to the user, comma-separated")

    # Common audit fields
    created_by: Mapped[str] = mapped_column(String(length=64), default=get_login_user, comment="Created by")
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now().astimezone(), comment="Creation timestamp"
    )
    updated_by: Mapped[str | None] = mapped_column(String(64), default=get_login_user, comment="Last updated by")
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTimeUTC(timezone=True),
        default=lambda: datetime.now().astimezone(),
        onupdate=lambda: datetime.now().astimezone(),
        comment="Last update timestamp",
    )
    deleted: Mapped[Deleted] = mapped_column(default=Deleted.N, comment="Deletion flag")
