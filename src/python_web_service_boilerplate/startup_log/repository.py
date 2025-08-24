from __future__ import annotations

from collections.abc import AsyncGenerator
from datetime import datetime

import arrow
from loguru import logger
from sqlalchemy import delete, select, update

from python_web_service_boilerplate.common.common_function import get_module_name
from python_web_service_boilerplate.configuration.database_configuration import (
    async_db_context,
)
from python_web_service_boilerplate.startup_log.models import StartupLog


async def save_startup_log(startup_log: StartupLog) -> StartupLog:
    async with async_db_context() as session:
        session.add(startup_log)
        await session.commit()
        await session.refresh(startup_log)  # Refresh to get the generated ID
        logger.info(f"Startup log saved: {startup_log}")
    return startup_log


async def update_shutdown_time(startup_log_id: int, shutdown_time: datetime | None = None) -> None:
    if shutdown_time is None:
        shutdown_time = datetime.now()

    async with async_db_context() as session:
        stmt = (
            update(StartupLog)
            .where(StartupLog.id == startup_log_id)
            .values(shutdown_time=shutdown_time, updated_at=datetime.now())
        )
        result = await session.execute(stmt)
        await session.commit()

        if result.rowcount == 1:
            logger.info(f"Updated shutdown time for startup log ID {startup_log_id}: {shutdown_time}")
        else:
            logger.warning(f"No startup log found with ID {startup_log_id}")


async def retain_startup_log() -> int:
    a_week_ago = arrow.now("local").shift(days=-7).floor("day").naive
    async with async_db_context() as session:
        result = await session.execute(delete(StartupLog).where(StartupLog.startup_time < a_week_ago))
    # the affected_rows is always 1 no matter how many rows were deleted
    logger.debug(
        f"The app [{get_module_name()}] retains recent 7 days of startup log. "
        f"Deleted {result.rowcount} records that are before {a_week_ago}"
    )
    return result.rowcount


async def stream_all_startup_logs() -> AsyncGenerator[StartupLog, None]:
    async with async_db_context() as session:
        result = await session.stream_scalars(select(StartupLog))
        async for log in result:
            logger.info(f"Retrieved startup logs, id: {log.id}")
            yield log
