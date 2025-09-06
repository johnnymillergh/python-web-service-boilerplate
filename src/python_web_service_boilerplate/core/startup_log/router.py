from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from python_web_service_boilerplate.core.auth.decorators import require_scopes
from python_web_service_boilerplate.core.startup_log.service import log_streamer

router = APIRouter(prefix="/api/v1")


@router.get("/startup_logs/stream")
@require_scopes({"core:read"})
async def stream_startup_logs() -> StreamingResponse:
    return StreamingResponse(log_streamer(), media_type="text/event-stream")
