import sys
from time import sleep

import pytest
from loguru import logger
from pytest_mock import MockFixture

from python_web_service_boilerplate.common.debounce_throttle import debounce, throttle

times_for_debounce: int = 0
times_for_debounce2: int = 0

times_for_throttle: int = 0
times_for_throttle2: int = 0
# Import current module for spying
current_module = sys.modules[__name__]


def test_debounce(mocker: MockFixture) -> None:
    spy = mocker.spy(current_module, "debounce_function")
    call_count: int = 3
    while call_count > 0:
        debounce_function(call_count)
        call_count -= 1
    spy.assert_called()
    assert times_for_debounce == 1
    result1 = debounce_function2()
    assert result1 is not None
    assert len(result1) > 0
    logger.info(result1)
    result2 = debounce_function2()
    assert result2 is None
    logger.info(result2)
    result3 = debounce_function2()
    assert result3 is None
    logger.info(result3)
    assert times_for_debounce2 == 1


def test_throttle(mocker: MockFixture) -> None:
    spy = mocker.spy(current_module, "throttle_function")
    call_count: int = 5
    try:
        while call_count > 0:
            throttle_function(call_count)
            call_count -= 1
            sleep(0.1)
    except Exception as ex:
        pytest.fail(f"Failed to test throttle_function(). {ex}")
    spy.assert_called()
    assert times_for_throttle >= 2
    throttled1 = throttle_function2()
    assert throttled1 is not None
    logger.info(throttled1)
    throttled2 = throttle_function2()
    assert throttled2 is None
    logger.info(throttled2)
    throttled3 = throttle_function2()
    assert throttled3 is None
    logger.info(throttled3)
    assert times_for_throttle2 == 1


@debounce(wait=1)
def debounce_function(a_int: int) -> None:
    global times_for_debounce
    times_for_debounce += 1
    logger.warning(f"'debounce_function' was called with {a_int}, times: {times_for_debounce}")


@debounce(wait=1)
def debounce_function2() -> str:
    global times_for_debounce2
    times_for_debounce2 += 1
    return f"debounce_function2 -> {times_for_debounce2}"


@throttle(limit=0.25)
def throttle_function(a_int: int) -> None:
    global times_for_throttle
    times_for_throttle += 1
    logger.warning(f"'throttle_function' was called with {a_int}, times: {times_for_throttle}")


@throttle(limit=0.25)
def throttle_function2() -> str:
    global times_for_throttle2
    times_for_throttle2 += 1
    return f"throttle_function2 -> {times_for_throttle}"
