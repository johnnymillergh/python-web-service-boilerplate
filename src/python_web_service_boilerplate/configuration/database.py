from __future__ import annotations

from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager, contextmanager
from typing import Any

import orjson
from loguru import logger
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

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

# Async engine and session setup
__async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    json_serializer=orjson_serializer,
    json_deserializer=orjson.loads,
    pool_use_lifo=True,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=application_conf.get_bool("database.sql_log_enabled"),
)

_AsyncSessionLocal = async_sessionmaker(
    bind=__async_engine, class_=AsyncSession, autocommit=False, autoflush=False, expire_on_commit=False
)


def get_db() -> Generator[Session, None, None]:
    with _SessionLocal() as session:
        yield session


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with _AsyncSessionLocal() as session:
        yield session


# Sync and Async context managers for manual session management
db_context = contextmanager(get_db)
async_db_context = asynccontextmanager(get_async_db)


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
        with db_context() as session:
            result = session.execute(text("SELECT 1;"))
            logger.warning("Creating all tables if not exist...")
            SQLModel.metadata.create_all(sync_engine)
        logger.warning(f"Sync connection initialized successfully, name: {sync_engine.name}, result: {result.all()}")
    except Exception as e:
        logger.error(f"Failed to initialize sync connection: {e!s}", e)
        raise
    try:
        # Test async connection
        async with async_db_context() as session:
            result = await session.execute(text("SELECT 1;"))
        logger.warning(
            f"Async connection initialized successfully, name: {__async_engine.name}, result: {result.all()}"
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
        await __async_engine.dispose()
        logger.warning(f"{__async_engine.name} async engine disposed")
    except Exception as e:
        logger.error(f"Error disposing async engine: {e!s}", e)
