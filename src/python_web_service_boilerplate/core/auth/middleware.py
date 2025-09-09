from loguru import logger
from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from python_web_service_boilerplate.core.auth.schemas import JWTPayload
from python_web_service_boilerplate.core.auth.service import UserService

_PUBLIC_ENDPOINTS = {
    "POST /api/v1/token",
    "POST /api/v1/users",
    "GET /health",
    "GET /docs",
    "GET /openapi.json",
    "GET /redoc",
}


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        api = f"{request.method} {request.url.path}"
        # Public endpoints that do not require authentication
        if api in _PUBLIC_ENDPOINTS:
            logger.info(f"Public endpoint: {api}, skipping auth")
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            logger.warning("No valid Authorization header found")
            return JSONResponse(status_code=401, content={"detail": "Not authenticated"})

        token = auth_header.split(" ")[1]
        try:
            jwt_payload: JWTPayload = UserService.verify_token(token)
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
        # Attach user to request
        request.state.username = jwt_payload.sub
        request.state.scopes = jwt_payload.scp
        return await call_next(request)
