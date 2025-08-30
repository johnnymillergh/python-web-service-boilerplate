from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class StartupLogSchema(BaseModel):
    id: int
    current_user: str
    hostname: str
    command_line: str
    current_working_directory: str
    startup_time: datetime
    shutdown_time: datetime | None = None
    created_by: str

    class Config:
        from_attributes = True
