from __future__ import annotations

from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager, contextmanager
from typing import TYPE_CHECKING, Any

import orjson
from loguru import logger
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from python_web_service_boilerplate.configuration.application_configuration import application_conf

if TYPE_CHECKING:
    from sqlalchemy.engine import Engine


Base = declarative_base()

DATABASE_URL = (
    f"postgresql+psycopg://{application_conf.get_string('database.username')}:{application_conf.get_string('database.password')}"
    f"@{application_conf.get_string('database.host')}:{application_conf.get_string('database.port')}/{application_conf.get_string('database.db_name')}"
)
ASYNC_DATABASE_URL = (
    f"postgresql+asyncpg://{application_conf.get_string('database.username')}:{application_conf.get_string('database.password')}"
    f"@{application_conf.get_string('database.host')}:{application_conf.get_string('database.port')}/{application_conf.get_string('database.db_name')}"
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
    connect_args={},
    echo=application_conf.get_bool("database.sql_log_enabled"),
)

_SessionLocal = sessionmaker(bind=sync_engine, autocommit=False, autoflush=False, expire_on_commit=False)

# Async engine and session setup
__async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    json_serializer=orjson_serializer,
    json_deserializer=orjson.loads,
    connect_args={},
    echo=application_conf.get_bool("database.sql_log_enabled"),
)

_AsyncSessionLocal = async_sessionmaker(bind=__async_engine, autocommit=False, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    """
    Synchronous database session generator for backward compatibility.
    For FastAPI to automatically manage the session lifecycle.
    """
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Asynchronous database session generator, for FastAPI to automatically manage the session lifecycle."""
    async with _AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Sync and Async context managers for manual session management
db_context = contextmanager(get_db)
async_db_context = asynccontextmanager(get_async_db)


async def configure() -> None:
    try:
        with db_context() as session:
            result = session.execute(text("SELECT 1"))
            Base.metadata.create_all(sync_engine)
        logger.warning(f"Sync connection initialized successfully, name: {sync_engine.name}, result: {result.all()}")
    except Exception as e:
        logger.error(f"Failed to initialize sync connection: {e!s}", e)
        raise
    try:
        # Test async connection
        async with async_db_context() as session:
            result = await session.execute(text("SELECT 1"))
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
