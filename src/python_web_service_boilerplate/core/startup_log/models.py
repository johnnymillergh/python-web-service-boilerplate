from __future__ import annotations

import os
import platform
from datetime import datetime

from sqlalchemy import BigInteger, Index, Integer, func
from sqlmodel import Field, SQLModel

from python_web_service_boilerplate.common.common_function import get_login_user, offline_environment
from python_web_service_boilerplate.core.common_models import Deleted


class StartupLog(SQLModel, table=True):
    """
    StartupLog model for tracking application startup events.

    This model captures detailed information about application startups including:
    - System information (hostname, user, working directory)
    - Command line arguments used to start the application
    - Timing information for startup and shutdown
    - Environment details for debugging and auditing
    """

    __tablename__ = "startup_log"

    id: int | None = Field(
        default=None,
        primary_key=True,
        sa_type=BigInteger if not offline_environment() else Integer,
        description="The primary key",
    )
    current_user: str = Field(
        max_length=64, index=True, default_factory=get_login_user, description="Current system user"
    )
    hostname: str = Field(
        max_length=64,
        index=True,
        default_factory=platform.node,
        description="The hostname where the application is running",
    )
    command_line: str = Field(description="The command line used to start the application")
    current_working_directory: str = Field(
        default_factory=os.getcwd, description="The current working directory of the application"
    )
    startup_time: datetime = Field(default_factory=datetime.now, description="When the application started")
    shutdown_time: datetime | None = Field(default=None, description="When the application shut down")

    # Common audit fields
    created_by: str = Field(max_length=64, default_factory=get_login_user, description="Created by")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_by: str | None = Field(max_length=64, default_factory=get_login_user, description="Last updated by")
    updated_at: datetime | None = Field(
        default_factory=datetime.now, sa_column_kwargs={"onupdate": func.now()}, description="Last update timestamp"
    )
    deleted: Deleted = Field(default=Deleted.N, description="Deletion flag")

    # Add indexes for common queries
    __table_args__ = (Index("ix_startup_logs_startup_time", "startup_time"),)

    def __str__(self) -> str:
        """String representation of the StartupLog instance."""
        return f"StartupLog({self.current_user} by {self.command_line} at {self.startup_time})"
