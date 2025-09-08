from typing import Any

import orjson
from advanced_alchemy.extensions.fastapi import (
    AsyncSessionConfig,
    SQLAlchemyAsyncConfig,
)
from advanced_alchemy.extensions.starlette import EngineConfig

from python_web_service_boilerplate.common.common_function import get_data_dir, get_module_name, offline_environment
from python_web_service_boilerplate.configuration.application import application_conf

ASYNC_DATABASE_URL = (
    (
        f"postgresql+asyncpg://{application_conf.get_string('database.username')}:{application_conf.get_string('database.password')}"
        f"@{application_conf.get_string('database.host')}:{application_conf.get_string('database.port')}/{application_conf.get_string('database.db_name')}"
    )
    if not offline_environment()
    else f"sqlite+aiosqlite:///{get_data_dir()}/{get_module_name()}.db"
)


def orjson_serializer(obj: Any) -> str:
    """
    Note that `orjson.dumps()` return byte array, while sqlalchemy expects string, thus `decode()` call.
    This function helped to solve JSON datetime conversion issue on JSONB column.
    """
    return orjson.dumps(obj, option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NAIVE_UTC).decode()


alchemy_config = SQLAlchemyAsyncConfig(
    connection_string=ASYNC_DATABASE_URL,
    session_config=AsyncSessionConfig(expire_on_commit=False),
    commit_mode="autocommit",
    create_all=True,
    engine_config=EngineConfig(
        json_serializer=orjson_serializer,
        json_deserializer=orjson.loads,
        pool_use_lifo=True,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=application_conf.get_bool("database.sql_log_enabled"),
    ),
)
