from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from python_web_service_boilerplate.system.startup_log.service import log_streamer

router = APIRouter(prefix="/api/v1")


@router.get("/startup_logs/stream")
async def stream_startup_logs() -> StreamingResponse:
    return StreamingResponse(log_streamer(), media_type="text/event-stream")
