from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from python_web_service_boilerplate.__main__ import alchemy
from python_web_service_boilerplate.core.auth.decorators import require_scopes
from python_web_service_boilerplate.core.startup_log.service import StartupLogService

router = APIRouter(prefix="/api/v1")


@router.get("/startup_logs/stream")
@require_scopes({"core:read"})
async def stream_startup_logs(
    startup_log_service: Annotated[StartupLogService, Depends(alchemy.provide_service(StartupLogService))],
) -> StreamingResponse:
    streamer = startup_log_service.log_streamer()
    return StreamingResponse(streamer, media_type="text/event-stream")
