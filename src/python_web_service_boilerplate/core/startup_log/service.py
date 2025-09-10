import asyncio
from collections.abc import AsyncGenerator

import orjson
from advanced_alchemy import service
from loguru import logger
from sqlalchemy import select

from python_web_service_boilerplate.common.middleware import get_current_request
from python_web_service_boilerplate.core.startup_log.models import StartupLog
from python_web_service_boilerplate.core.startup_log.repository import Repository
from python_web_service_boilerplate.core.startup_log.schemas import StartupLogSchema


class StartupLogService(service.SQLAlchemyAsyncRepositoryService[StartupLog, Repository]):
    repository_type = Repository

    async def log_streamer(self) -> AsyncGenerator[str, None]:
        logger.info(f"{get_current_request().state.username} is accessing startup log stream")
        result = await self.repository.session.stream_scalars(select(StartupLog))
        async for log in result:
            await asyncio.sleep(0.1)
            logger.info(f"Retrieved startup logs, id: {log.id}")
            yield f"data: {orjson.dumps(StartupLogSchema.model_validate(log).model_dump()).decode()}\n\n"
