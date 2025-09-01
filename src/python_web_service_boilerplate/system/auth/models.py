from __future__ import annotations

from datetime import datetime

from sqlalchemy import func
from sqlmodel import Field, SQLModel

from python_web_service_boilerplate.common.common_function import get_login_user
from python_web_service_boilerplate.system.common_models import Deleted


class User(SQLModel, table=True):
    __tablename__ = "user"

    id: int | None = Field(default=None, primary_key=True, description="The primary key")
    username: str = Field(max_length=64, index=True, unique=True, description="The username")
    password: str = Field(max_length=512, description="The password")
    email: str = Field(max_length=256, index=True, description="The email address")
    full_name: str = Field(max_length=128, description="The full name of the user")

    # Common audit fields
    created_by: str = Field(default_factory=get_login_user, max_length=64, description="Created by")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_by: str | None = Field(default_factory=get_login_user, max_length=64, description="Last updated by")
    updated_at: datetime | None = Field(
        default_factory=datetime.now, sa_column_kwargs={"onupdate": func.now()}, description="Last update timestamp"
    )
    deleted: Deleted = Field(default=Deleted.N, description="Deletion flag")
