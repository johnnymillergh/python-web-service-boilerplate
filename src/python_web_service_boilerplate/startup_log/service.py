import asyncio
from collections.abc import AsyncGenerator

import orjson

from python_web_service_boilerplate.startup_log.repository import stream_all_startup_logs
from python_web_service_boilerplate.startup_log.schemas import StartupLogSchema


async def log_streamer() -> AsyncGenerator[str, None]:
    async for log in stream_all_startup_logs():
        await asyncio.sleep(0.1)
        yield f"data: {orjson.dumps(StartupLogSchema.model_validate(log).model_dump()).decode()}\n\n"
