from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from loguru import logger

from python_web_service_boilerplate.__main__ import alchemy
from python_web_service_boilerplate.common.middleware import get_current_request
from python_web_service_boilerplate.core.auth.decorators import require_scopes
from python_web_service_boilerplate.core.startup_log.service import StartupLogService

router = APIRouter(prefix="/api/v1")


@router.get("/startup_logs/stream")
@require_scopes({"core:read"})
async def stream_startup_logs() -> StreamingResponse:
    logger.info(f"{get_current_request().state.username} is accessing startup log stream")
    return StreamingResponse(StartupLogService.log_streamer(), media_type="text/event-stream")


@router.get("/startup_logs/broken_stream")
@require_scopes({"core:read"})
async def broken_stream_startup_logs(
    startup_log_service: Annotated[StartupLogService, Depends(alchemy.provide_service(StartupLogService))],
) -> StreamingResponse:
    logger.info(f"{get_current_request().state.username} is accessing startup log stream")
    count = await startup_log_service.count()
    logger.info(f"There are {count} startup logs in the database")
    return StreamingResponse(startup_log_service.log_streamer_broken(), media_type="text/event-stream")
