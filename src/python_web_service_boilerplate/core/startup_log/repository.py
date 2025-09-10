from __future__ import annotations

from collections.abc import AsyncGenerator
from datetime import datetime

import arrow
from advanced_alchemy import repository
from loguru import logger
from sqlalchemy import delete, select
from sqlmodel import and_

from python_web_service_boilerplate.common.common_function import get_module_name
from python_web_service_boilerplate.configuration.database import alchemy_config
from python_web_service_boilerplate.core.startup_log.models import StartupLog


class Repository(repository.SQLAlchemyAsyncRepository[StartupLog]):
    model_type = StartupLog

    @staticmethod
    async def stream_all_startup_logs() -> AsyncGenerator[StartupLog, None]:
        async with alchemy_config.get_session() as session:
            result = await session.stream_scalars(select(StartupLog))
            async for log in result:
                logger.info(f"Retrieved startup logs, id: {log.id}")
                yield log


async def save_startup_log(startup_log: StartupLog) -> StartupLog:
    async with alchemy_config.get_session() as db:
        db.add(startup_log)
        await db.commit()
        await db.refresh(startup_log)  # Refresh to get the generated ID
        logger.info(f"Startup log saved: {startup_log}")
    return startup_log


async def update_shutdown_time(startup_log: StartupLog | None) -> None:
    if not startup_log:
        logger.warning("No startup log found to update shutdown time")
        return
    async with alchemy_config.get_session() as db:
        startup_log.shutdown_time = datetime.now().astimezone()
        db.add(startup_log)
        await db.commit()
        logger.info(f"Updated shutdown time for startup log ID {startup_log.id}: {startup_log.shutdown_time}")


async def retain_startup_log() -> None:
    a_week_ago = arrow.now("local").shift(days=-7).floor("day").datetime
    async with alchemy_config.get_session() as session:
        await session.execute(delete(StartupLog).where(and_(StartupLog.startup_time < a_week_ago)))
    # the affected_rows is always 1 no matter how many rows were deleted
    logger.debug(
        f"The app [{get_module_name()}] retains recent 7 days of startup log. "
        f"Deleted records that are before {a_week_ago}"
    )
