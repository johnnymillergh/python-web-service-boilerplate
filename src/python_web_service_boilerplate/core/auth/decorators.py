import inspect
from functools import wraps
from http import HTTPStatus
from typing import Any, Callable, TypeVar

from loguru import logger
from starlette.exceptions import HTTPException

from python_web_service_boilerplate.common.middleware import get_current_request

F = TypeVar("F", bound=Callable[..., Any])


def require_scopes(required_scopes: set[str]) -> Callable[[F], F]:
    """
    Decorator to require specific scopes with middleware dependency check.
    If the user has any of the required scopes, access is granted.
    Works with both sync and async functions.
    """

    def decorator(func: F) -> Any:
        def _check_scopes() -> None:
            """Common scope checking logic."""
            logger.debug(f"@require_scopes checking scopes: {required_scopes}")
            request = get_current_request()
            scopes_str = getattr(request.state, "scopes", "")
            user_scopes = set(scopes_str.split(","))
            if "admin" in user_scopes:
                logger.debug("User has admin scope, all access granted")
                return
            intersection = required_scopes.intersection(user_scopes)
            if len(intersection) == 0:
                logger.warning(f"User missing scopes required: {required_scopes}. User has: {user_scopes}")
                joined_scopes = " / ".join(required_scopes)
                raise HTTPException(
                    status_code=HTTPStatus.FORBIDDEN.value,
                    detail=f"Insufficient permissions. Required scopes: {joined_scopes}",
                    headers={"WWW-Authenticate": f'Bearer scope="{joined_scopes}"'},
                )
            logger.debug(f"Scope validation successful. Required: {required_scopes}, User has: {user_scopes}")

        if inspect.iscoroutinefunction(func):
            # Async function wrapper
            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                _check_scopes()
                return await func(*args, **kwargs)

            return async_wrapper

        # Sync function wrapper
        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            _check_scopes()
            return func(*args, **kwargs)

        return sync_wrapper

    return decorator


def admin_required(func: F) -> F:
    """Decorator to require admin scope."""
    return require_scopes({"admin"})(func)
