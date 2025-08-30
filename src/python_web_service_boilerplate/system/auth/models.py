from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Enum, Integer, String

from python_web_service_boilerplate.common.common_function import get_login_user, offline_environment
from python_web_service_boilerplate.configuration.database_configuration import Base
from python_web_service_boilerplate.system.common_models import Deleted


class User(Base):
    __tablename__ = "user"

    id = (
        Column(BigInteger, primary_key=True, index=True, comment="The primary key")
        if not offline_environment()
        else Column(Integer, primary_key=True, index=True, comment="The primary key")
    )
    username = Column(String(64), nullable=False, index=True, unique=True, comment="The username")
    password = Column(String(512), nullable=False, comment="The password")
    email = Column(String(256), nullable=False, index=True, comment="The email address")
    full_name = Column(String(128), nullable=False, comment="The full name of the user")

    # Common audit fields
    created_by = Column(String(64), nullable=True, comment="Created by", default=get_login_user)
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment="Creation timestamp")
    updated_by = Column(String(64), nullable=True, comment="Last updated by", default=get_login_user)
    updated_at = Column(
        DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment="Last update timestamp"
    )
    deleted = Column(Enum(Deleted), nullable=False, default=Deleted.N, comment="Deletion flag")
