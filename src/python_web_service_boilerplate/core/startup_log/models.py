from __future__ import annotations

import os
import platform
from datetime import datetime, timezone

import pytz
from advanced_alchemy import base
from sqlalchemy import BigInteger, Index, Integer, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import String, Text
from sqlmodel import Field, SQLModel

from python_web_service_boilerplate.common.common_function import get_login_user, offline_environment
from python_web_service_boilerplate.core.common_models import Deleted


class StartupLog(base.BigIntBase):
    """
    StartupLog model for tracking application startup events.

    This model captures detailed information about application startups including:
    - System information (hostname, user, working directory)
    - Command line arguments used to start the application
    - Timing information for startup and shutdown
    - Environment details for debugging and auditing
    """
    __tablename__ = "startup_log"

    current_user: Mapped[str] = mapped_column(
        String(length=64), index=True, default=get_login_user, comment="Current system user"
    )
    hostname: Mapped[str] = mapped_column(
        String(length=64), index=True, default=platform.node, comment="The hostname where the application is running"
    )
    command_line: Mapped[str] = mapped_column(Text(), comment="The command line used to start the application")
    current_working_directory: Mapped[str] = mapped_column(
        Text(), default=os.getcwd, comment="The current working directory of the application"
    )
    startup_time: Mapped[datetime] = mapped_column(
        default=func.now(), comment="When the application started"
    )
    shutdown_time: Mapped[datetime | None] = mapped_column(
        default=None, comment="When the application shut down"
    )

    # Common audit fields
    created_by: Mapped[str] = mapped_column(
        String(length=64), default=get_login_user, comment="Created by"
    )
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(), comment="Creation timestamp"
    )
    updated_by: Mapped[str | None] = mapped_column(String(length=64), default=get_login_user, comment="Last updated by")
    updated_at: Mapped[datetime | None] = mapped_column(default=func.now(), onupdate=func.now(), comment="Last update timestamp")
    deleted: Mapped[Deleted] = mapped_column(default=Deleted.N, comment="Deletion flag")

    __table_args__ = (Index("ix_startup_logs_startup_time", "startup_time"),)

    def __str__(self) -> str:
        return f"StartupLog({self.current_user} by {self.command_line} at {self.startup_time})"
