import asyncio
from collections.abc import AsyncGenerator

import orjson
from loguru import logger

from python_web_service_boilerplate.common.middleware import get_current_request
from python_web_service_boilerplate.system.startup_log.repository import stream_all_startup_logs
from python_web_service_boilerplate.system.startup_log.schemas import StartupLogSchema


async def log_streamer() -> AsyncGenerator[str, None]:
    logger.info(f"{get_current_request().state.username} is accessing startup log stream")
    async for log in stream_all_startup_logs():
        await asyncio.sleep(0.1)
        yield f"data: {orjson.dumps(StartupLogSchema.model_validate(log).model_dump()).decode()}\n\n"
