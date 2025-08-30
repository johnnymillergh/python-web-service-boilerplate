from collections.abc import Generator
from typing import TYPE_CHECKING, Any

import pytest
from loguru import logger
from pyinstrument.profiler import Profiler
from starlette.testclient import TestClient

from python_web_service_boilerplate.__main__ import app
from python_web_service_boilerplate.common.common_function import PROJECT_ROOT_PATH, get_module_name

if TYPE_CHECKING:
    from _pytest.nodes import Node


@pytest.fixture
def test_client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


def pytest_html_report_title(report: Any) -> None:
    """
    pytest-html title configuration.

    https://pytest-html.readthedocs.io/en/latest/user_guide.html#user-guide
    """
    report.title = f"Pytest Report of {get_module_name()}"


@pytest.fixture(autouse=True)
def auto_profile(request: Any) -> Generator[Any, Any, None]:
    """
    Generate an HTML file for each test node in your test suite inside the .profiles directory.

    https://pyinstrument.readthedocs.io/en/latest/guide.html#profile-pytest-tests
    """
    profile_root = PROJECT_ROOT_PATH / "build/.profiles"
    logger.info("Starting to profile Pytest unit tests...")
    # Turn profiling on
    profiler = Profiler()
    profiler.start()

    yield  # Run test

    profiler.stop()
    node: Node = request.node
    profile_html_path = profile_root / f"{node.path.parent.relative_to(PROJECT_ROOT_PATH)}"
    if not profile_html_path.exists():
        # If parents=False (the default), a missing parent raises FileNotFoundError.
        # If exist_ok=False (the default), FileExistsError is raised if the target directory already exists.
        profile_html_path.mkdir(parents=True, exist_ok=True)
    results_file = profile_html_path / f"{node.name}.html"
    with results_file.open("w", encoding="utf-8") as f_html:
        f_html.write(profiler.output_html())
        logger.info(f"Generated profile result: [{results_file}]")
