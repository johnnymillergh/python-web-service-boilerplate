from __future__ import annotations

import os
import platform
import sys
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import timedelta
from pathlib import Path

from fastapi import FastAPI
from loguru import logger

from python_web_service_boilerplate.common.common_function import get_module_name
from python_web_service_boilerplate.common.middleware import TraceIDMiddleware
from python_web_service_boilerplate.common.router_loader import include_routers
from python_web_service_boilerplate.configuration.application_configuration import (
    configure as configure_application,
)
from python_web_service_boilerplate.configuration.application_configuration import pyproject_toml
from python_web_service_boilerplate.configuration.apscheduler_configuration import (
    cleanup as apscheduler_cleanup,
)
from python_web_service_boilerplate.configuration.apscheduler_configuration import (
    configure as configure_apscheduler,
)
from python_web_service_boilerplate.configuration.database_configuration import (
    cleanup as database_cleanup,
)
from python_web_service_boilerplate.configuration.database_configuration import (
    configure as configure_database,
)
from python_web_service_boilerplate.configuration.loguru_configuration import (
    configure as configure_loguru,
)
from python_web_service_boilerplate.configuration.thread_pool_configuration import (
    cleanup as thread_pool_cleanup,
)
from python_web_service_boilerplate.configuration.thread_pool_configuration import (
    configure as configure_thread_pool,
)
from python_web_service_boilerplate.startup_log.models import StartupLog
from python_web_service_boilerplate.startup_log.repository import (
    retain_startup_log,
    save_startup_log,
    update_shutdown_time,
)

__start_time = time.perf_counter()
__startup_log_id: int | None = None  # Track the startup log ID for shutdown updates


# noinspection PyShadowingNames
async def startup(app: FastAPI) -> None:
    """Call this function to start the application and do all the preparations and configurations."""
    logger.info(
        f"Starting {get_module_name()} using Python {platform.python_version()} on "
        f"{platform.node()} with PID {os.getpid()} ({Path(__file__).parent})"
    )

    # Configuration
    configure_application()
    configure_loguru()
    await configure_database()
    configure_thread_pool()
    configure_apscheduler()

    # Scanning routers
    include_routers(app, get_module_name())

    startup_log = StartupLog(command_line=" ".join(sys.argv))
    saved_startup_log = await save_startup_log(startup_log)
    global __startup_log_id
    __startup_log_id = saved_startup_log.id

    elapsed = time.perf_counter() - __start_time
    logger.info(
        f"Started {get_module_name()}@{pyproject_toml['tool']['poetry']['version']} in {timedelta(seconds=elapsed)}"
    )


async def shutdown() -> None:
    """Register `finalize()` function to be executed upon normal program termination."""
    logger.warning(f"Stopping {get_module_name()}, releasing system resources")

    await retain_startup_log()
    thread_pool_cleanup()
    apscheduler_cleanup()
    # Update shutdown time in startup log if we have an ID
    if __startup_log_id is not None:
        try:
            await update_shutdown_time(__startup_log_id)
        except Exception as e:
            logger.error(f"Failed to update shutdown time for startup log {__startup_log_id}: {e}")
    await database_cleanup()
    end_elapsed = time.perf_counter() - __start_time
    logger.info(f"Stopped {get_module_name()}, running for {timedelta(seconds=end_elapsed)} in total")


# noinspection PyUnusedLocal,PyShadowingNames
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting up application...")
    try:
        await startup(app)
        yield  # Application runs here
    finally:
        logger.info("Shutting down application...")
        await shutdown()


app = FastAPI(lifespan=lifespan)
# Add trace ID middleware to automatically handle request tracing
app.add_middleware(TraceIDMiddleware)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": f"Hello World from {get_module_name()}"}


if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run(app, host="localhost", port=8080, log_config=None, log_level=None)
