from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

import orjson
from advanced_alchemy.extensions.fastapi import (
    AsyncSessionConfig,
    SQLAlchemyAsyncConfig,
)
from advanced_alchemy.extensions.starlette import EngineConfig
from loguru import logger
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from python_web_service_boilerplate.common.common_function import get_data_dir, get_module_name, offline_environment
from python_web_service_boilerplate.configuration.application import application_conf

DATABASE_URL = (
    (
        f"postgresql+psycopg://{application_conf.get_string('database.username')}:{application_conf.get_string('database.password')}"
        f"@{application_conf.get_string('database.host')}:{application_conf.get_string('database.port')}/{application_conf.get_string('database.db_name')}"
    )
    if not offline_environment()
    else f"sqlite:///{get_data_dir()}/{get_module_name()}.db"
)
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


# Synchronous engine and session setup (backward compatibility)
sync_engine: Engine = create_engine(
    DATABASE_URL,
    json_serializer=orjson_serializer,
    json_deserializer=orjson.loads,
    pool_use_lifo=True,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=application_conf.get_bool("database.sql_log_enabled"),
)
_SessionLocal = sessionmaker(
    bind=sync_engine, class_=Session, autocommit=False, autoflush=False, expire_on_commit=False
)


@contextmanager
def get_sync_db() -> Generator[Session, None, None]:
    """Sync context managers for manual session management."""
    with _SessionLocal() as session:
        yield session


async def configure() -> None:
    """
    Initialize the database connection and create all tables if not exist.
    >>> from sqlalchemy.engine.create import create_engine
    >>> create_engine()
    >>> from sqlalchemy.ext.asyncio import create_async_engine
    >>> create_async_engine()
    >>> from sqlalchemy.pool.impl import QueuePool
    >>> # QueuePool is the default sync pool implementation
    >>> QueuePool.__init__()
    >>> from sqlalchemy.pool.impl import AsyncAdaptedQueuePool
    >>> # AsyncAdaptedQueuePool is the default async pool implementation
    >>> AsyncAdaptedQueuePool.__init__()
    Default the database connection configuration above.
    """
    try:
        with get_sync_db() as session:
            result = session.execute(text("SELECT 1;"))
        logger.warning(f"Sync connection initialized successfully, name: {sync_engine.name}, result: {result.all()}")
    except Exception as e:
        logger.error(f"Failed to initialize sync connection: {e!s}", e)
        raise
    try:
        # Test async connection
        async with alchemy_config.get_session() as session:
            result = await session.execute(text("SELECT 1;"))
        logger.warning(
            f"Async connection initialized successfully, name: {alchemy_config.get_engine().name}, "
            f"result: {result.all()}"
        )
    except Exception as e:
        logger.error(f"Failed to initialize async connection: {e!s}", e)
        raise


async def cleanup() -> None:
    try:
        sync_engine.dispose()
        logger.warning(f"{sync_engine.name} sync engine disposed")
    except Exception as e:
        logger.error(f"Error disposing sync engine: {e!s}", e)
    try:
        await alchemy_config.close_engine()
        logger.warning(f"{alchemy_config.get_engine().name} async engine disposed")
    except Exception as e:
        logger.error(f"Error disposing async engine: {e!s}", e)
