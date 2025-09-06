import functools
import inspect
import os
import time
from datetime import timedelta
from typing import Any, Callable, TypeVar

import psutil
from loguru import logger

R = TypeVar("R")


def elapsed_time(level: str = "INFO") -> Callable[..., Any]:
    """
    The decorator to monitor the elapsed time of both sync and async functions.

    Usage:

    * decorate the function with `@elapsed_time()` to profile the function with INFO log
    >>> @elapsed_time()
    >>> def some_function():
    >>>    pass

    >>> @elapsed_time()
    >>> async def some_async_function():
    >>>    pass

    * decorate the function with `@elapsed_time("DEBUG")` to profile the function with DEBUG log
    >>> @elapsed_time("DEBUG")
    >>> def some_function():
    >>>    pass

    >>> @elapsed_time("DEBUG")
    >>> async def some_async_function():
    >>>    pass

    https://stackoverflow.com/questions/12295974/python-decorators-just-syntactic-sugar

    :param level: logging level, default is "INFO". Available values: ["TRACE", "DEBUG", "INFO", "WARNING", "ERROR"]
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        if inspect.iscoroutinefunction(func):
            # Handle async functions
            # noinspection PyUnresolvedReferences
            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                start_time = time.perf_counter()
                try:
                    return_value = await func(*args, **kwargs)
                except Exception as e:
                    elapsed = time.perf_counter() - start_time
                    logger.log(
                        level,
                        f"{func.__module__}.{func.__qualname__}() -> elapsed time: {timedelta(seconds=elapsed)}",
                    )
                    raise e
                elapsed = time.perf_counter() - start_time
                logger.log(
                    level,
                    f"{func.__module__}.{func.__qualname__}() -> elapsed time: {timedelta(seconds=elapsed)}",
                )
                return return_value

            return async_wrapper

        # Handle sync functions
        # noinspection PyUnresolvedReferences
        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.perf_counter()
            try:
                return_value = func(*args, **kwargs)
            except Exception as e:
                logger.exception(f"Exception raised when executing function: {func.__qualname__}(). Exception: {e}")
                elapsed = time.perf_counter() - start_time
                logger.log(
                    level,
                    f"{func.__module__}.{func.__qualname__}() -> elapsed time: {timedelta(seconds=elapsed)}",
                )
                raise e
            elapsed = time.perf_counter() - start_time
            logger.log(
                level,
                f"{func.__module__}.{func.__qualname__}() -> elapsed time: {timedelta(seconds=elapsed)}",
            )
            return return_value

        return sync_wrapper

    return decorator


def _get_memory_usage() -> int:
    """
    Gets the usage of memory.

    :return: memory usage in bytes
    """
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    return mem_info.rss


def _get_cpu_usage() -> float:
    """
    Getting cpu_percent non-blocking (percentage since last call).

    :return: CPU usage
    """
    return psutil.cpu_percent()


def mem_profile(level: str = "INFO") -> Callable[..., Any]:
    """
    The decorator to monitor the memory usage of both sync and async functions.

    Usage:

    * decorate the function with `@mem_profile()` to profile the function with INFO log
    >>> @mem_profile()
    >>> def some_function():
    >>>    pass

    >>> @mem_profile()
    >>> async def some_async_function():
    >>>    pass

    * decorate the function with `@mem_profile("DEBUG")` to profile the function with DEBUG log
    >>> @mem_profile("DEBUG")
    >>> def some_function():
    >>>    pass

    >>> @mem_profile("DEBUG")
    >>> async def some_async_function():
    >>>    pass

    https://stackoverflow.com/questions/12295974/python-decorators-just-syntactic-sugar

    :param level: logging level, default is "INFO". Available values: ["TRACE", "DEBUG", "INFO", "WARNING", "ERROR"]
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        if inspect.iscoroutinefunction(func):
            # Handle async functions
            # noinspection PyUnresolvedReferences
            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                mem_before = _get_memory_usage()
                try:
                    return_value = await func(*args, **kwargs)
                except Exception as e:
                    mem_after = _get_memory_usage()
                    logger.log(
                        level,
                        f"{func.__module__}.{func.__qualname__}() -> Mem before: {mem_before}, mem after: {mem_after}, "
                        f"delta: {(mem_after - mem_before) / (1024 * 1024):.2f} MB",
                    )
                    raise e
                mem_after = _get_memory_usage()
                logger.log(
                    level,
                    f"{func.__module__}.{func.__qualname__}() -> Mem before: {mem_before}, mem after: {mem_after}, "
                    f"delta: {(mem_after - mem_before) / (1024 * 1024):.2f} MB",
                )
                return return_value

            return async_wrapper

        # Handle sync functions
        # noinspection PyUnresolvedReferences
        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            mem_before = _get_memory_usage()
            try:
                return_value = func(*args, **kwargs)
            except Exception as e:
                mem_after = _get_memory_usage()
                logger.log(
                    level,
                    f"{func.__module__}.{func.__qualname__}() -> Mem before: {mem_before}, mem after: {mem_after}, "
                    f"delta: {(mem_after - mem_before) / (1024 * 1024):.2f} MB",
                )
                raise e
            mem_after = _get_memory_usage()
            logger.log(
                level,
                f"{func.__module__}.{func.__qualname__}() -> Mem before: {mem_before}, mem after: {mem_after}, "
                f"delta: {(mem_after - mem_before) / (1024 * 1024):.2f} MB",
            )
            return return_value

        return sync_wrapper

    return decorator


def cpu_profile(level: str = "INFO") -> Callable[..., Any]:
    """
    The decorator to monitor the CPU usage of both sync and async functions.

    Usage:

    * decorate the function with `@cpu_profile()` to profile the function with INFO log
    >>> @cpu_profile()
    >>> def some_function():
    >>>    pass

    >>> @cpu_profile()
    >>> async def some_async_function():
    >>>    pass

    * decorate the function with `@cpu_profile("DEBUG")` to profile the function with DEBUG log
    >>> @cpu_profile("DEBUG")
    >>> def some_function():
    >>>    pass

    >>> @cpu_profile("DEBUG")
    >>> async def some_async_function():
    >>>    pass

    https://stackoverflow.com/questions/12295974/python-decorators-just-syntactic-sugar

    :param level: logging level, default is "INFO". Available values: ["TRACE", "DEBUG", "INFO", "WARNING", "ERROR"]
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        if inspect.iscoroutinefunction(func):
            # Handle async functions
            # noinspection PyUnresolvedReferences
            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                cpu_before = _get_cpu_usage()
                try:
                    return_value = await func(*args, **kwargs)
                except Exception as e:
                    cpu_after = _get_cpu_usage()
                    logger.log(
                        level,
                        f"{func.__module__}.{func.__qualname__}() -> CPU before: {cpu_before}, CPU after: {cpu_after}, "
                        f"delta: {(cpu_after - cpu_before):.2f}",
                    )
                    raise e
                cpu_after = _get_cpu_usage()
                logger.log(
                    level,
                    f"{func.__module__}.{func.__qualname__}() -> CPU before: {cpu_before}, CPU after: {cpu_after}, "
                    f"delta: {(cpu_after - cpu_before):.2f}",
                )
                return return_value

            return async_wrapper

        # Handle sync functions
        # noinspection PyUnresolvedReferences
        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            cpu_before = _get_cpu_usage()
            try:
                return_value = func(*args, **kwargs)
            except Exception as e:
                cpu_after = _get_cpu_usage()
                logger.log(
                    level,
                    f"{func.__module__}.{func.__qualname__}() -> CPU before: {cpu_before}, CPU after: {cpu_after}, "
                    f"delta: {(cpu_after - cpu_before):.2f}",
                )
                raise e
            cpu_after = _get_cpu_usage()
            logger.log(
                level,
                f"{func.__module__}.{func.__qualname__}() -> CPU before: {cpu_before}, CPU after: {cpu_after}, "
                f"delta: {(cpu_after - cpu_before):.2f}",
            )
            return return_value

        return sync_wrapper

    return decorator
