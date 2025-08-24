from __future__ import annotations

import os
import platform
from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Index, String, Text

from python_web_service_boilerplate.common.common_function import get_login_user
from python_web_service_boilerplate.configuration.database_configuration import Base


class StartupLog(Base):
    """
    StartupLog model for tracking application startup events.

    This model captures detailed information about application startups including:
    - System information (hostname, user, working directory)
    - Command line arguments used to start the application
    - Timing information for startup and shutdown
    - Environment details for debugging and auditing
    """

    __tablename__ = "startup_log"

    id = Column(BigInteger, primary_key=True, index=True)

    # System information fields
    current_user = Column(String(64), nullable=False, index=True, comment="Current system user", default=get_login_user)

    hostname = Column(
        String(64),
        nullable=False,
        index=True,
        comment="The hostname where the application is running",
        default=platform.node,
    )

    command_line = Column(Text, nullable=False, comment="The command line used to start the application")

    current_working_directory = Column(
        Text, nullable=False, default=os.getcwd, comment="The current working directory of the application"
    )

    startup_time = Column(DateTime, nullable=False, default=datetime.now, comment="When the application started")

    shutdown_time = Column(DateTime, nullable=True, comment="When the application shut down")

    # Common audit fields
    created_by = Column(String(50), nullable=False, default=get_login_user)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_by = Column(String(50), nullable=True, default=get_login_user)
    updated_at = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now)

    # Add indexes for common queries
    __table_args__ = (
        Index("ix_startup_logs_hostname_startup_time", "hostname", "startup_time"),
        Index("ix_startup_logs_user_startup_time", "current_user", "startup_time"),
    )

    def __str__(self) -> str:
        """String representation of the StartupLog instance."""
        return f"StartupLog({self.current_user} by {self.command_line} at {self.startup_time})"

    @property
    def execution_duration_ms(self) -> float | None:
        """Calculate execution duration in milliseconds."""
        if self.shutdown_time and self.startup_time:
            return (self.shutdown_time - self.startup_time).total_seconds() * 1000
        return None
