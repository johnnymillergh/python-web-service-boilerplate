from loguru import logger
from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from python_web_service_boilerplate.system.auth.service import verify_token


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        api = f"{request.method} {request.url.path}"
        # Public endpoints that do not require authentication
        if api in {"POST /api/v1/token", "POST /api/v1/users", "GET /health", "GET /docs"}:
            logger.info(f"Public endpoint: {api}, skipping auth")
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            logger.warning("Auth header is missing")
            return JSONResponse(status_code=401, content={"detail": "Not authenticated"})

        token = auth_header.split(" ")[1]
        try:
            username = verify_token(token)
            # Attach user to request
            request.state.username = username
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={"detail": e.detail})

        return await call_next(request)
