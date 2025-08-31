from __future__ import annotations

from contextvars import ContextVar
from typing import Any

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from python_web_service_boilerplate.common.trace import clear_trace_id, generate_trace_id, set_trace_id

# Create a context variable
_http_request_context: ContextVar[Request | None] = ContextVar("http_request")


class TraceIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle trace ID for each HTTP request.

    The middleware will:
    1. Extract trace ID from request headers (X-Trace-ID) or generate a new one
    2. Set it in the context for the duration of the request
    3. Add it to the response headers
    4. Log request start and end with trace ID
    """

    TRACE_ID_HEADER = "X-Trace-ID"

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Extract trace ID from headers or generate a new one
        trace_id = request.headers.get(self.TRACE_ID_HEADER)
        if not trace_id:
            trace_id = generate_trace_id()

        # Set trace ID in context
        set_trace_id(trace_id)

        _http_request_context.set(request)

        # Log request start
        logger.info(f"Request started: {request.method} {request.url.path}")

        try:
            # Process the request
            response = await call_next(request)
        except Exception as e:
            # Log error with trace ID
            logger.error(f"Request failed: {request.method} {request.url.path} - Error: {e!s}", e)
            raise e
        else:
            # Add trace ID to response headers
            response.headers[self.TRACE_ID_HEADER] = trace_id
            # Log request completion
            logger.info(f"Request completed: {request.method} {request.url.path} - Status: {response.status_code}")
            return response
        finally:
            # Clean up context
            clear_trace_id()
            _http_request_context.set(None)


def get_current_request() -> Request:
    """Get the current HTTP request from context."""
    http_request = _http_request_context.get()
    if http_request:
        return http_request
    return Request(scope={})


# Alternative function-based middleware for other frameworks
def trace_id_middleware(request: Request, response: Response, call_next: RequestResponseEndpoint) -> Any:
    """Function-based middleware for frameworks that don't use class-based middleware."""
    # Extract trace ID from headers or generate a new one
    trace_id = getattr(request, "headers", {}).get("X-Trace-ID")
    if not trace_id:
        trace_id = generate_trace_id()

    # Set trace ID in context
    set_trace_id(trace_id)

    try:
        # Log request start
        method = getattr(request, "method", "UNKNOWN")
        path = getattr(request, "path", getattr(request, "url", "UNKNOWN"))
        logger.info(f"Request started: {method} {path}")

        # Process the request
        result = call_next(request)
    except Exception as e:
        logger.error(
            f"Request failed: {getattr(request, 'method', 'UNKNOWN')} {getattr(request, 'path', 'UNKNOWN')} - "
            f"Error: {e!s}",
            e,
        )
        raise e
    else:
        # Add trace ID to response headers if possible
        if hasattr(response, "headers"):
            response.headers["X-Trace-ID"] = trace_id

        # Log request completion
        logger.info(f"Request completed: {method} {path}")

        return result
    finally:
        # Clean up context
        clear_trace_id()
