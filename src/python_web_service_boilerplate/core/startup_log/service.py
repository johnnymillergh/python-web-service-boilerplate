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

    @staticmethod
    async def log_streamer() -> AsyncGenerator[str, None]:
        """
        A demo implementation of server-sent events (SSE).
        ! WARNING: With advanced-alchemy, we have to use `alchemy_config.get_session()` to stream the logs from the
        !  database. Otherwise, SQLAlchemy will throw an error:
        sqlalchemy.exc.InvalidRequestError: Object <StartupLog at 0x23645e93d90> cannot be converted to 'persistent'
        state, as this identity map is no longer valid.  Has the owning Session been closed? (Background on this error
        at: https://sqlalche.me/e/20/lkrp).
        """
        async for log in Repository.stream_all_startup_logs():
            await asyncio.sleep(0.1)
            yield f"data: {orjson.dumps(StartupLogSchema.model_validate(log).model_dump()).decode()}\n\n"

    async def log_streamer_broken(self) -> AsyncGenerator[str, None]:
        """
        A broken demo implementation of server-sent events (SSE).
        ! WARNING: With advanced-alchemy, we use `repository.session` to stream the logs from the database.
        !  This is expected to happen, SQLAlchemy will throw an error:
        sqlalchemy.exc.InvalidRequestError: Object <StartupLog at 0x23645e93d90> cannot be converted to 'persistent'
        state, as this identity map is no longer valid.  Has the owning Session been closed? (Background on this error
        at: https://sqlalche.me/e/20/lkrp).
        """
        logger.info(f"{get_current_request().state.username} is accessing startup log stream")
        result = await self.repository.session.stream_scalars(select(StartupLog))
        async for log in result:
            await asyncio.sleep(0.1)
            logger.info(f"[Broken] Retrieved startup logs, id: {log.id}")
            yield f"data: {orjson.dumps(StartupLogSchema.model_validate(log).model_dump()).decode()}\n\n"
