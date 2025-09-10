from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
import pytest_asyncio
from _pytest.nodes import Node
from fastapi_cloud_cli.commands.login import TokenResponse
from httpx import ASGITransport, AsyncClient
from loguru import logger
from pyinstrument.profiler import Profiler
from sqlalchemy.ext.asyncio.session import AsyncSession
from starlette.testclient import TestClient

from python_web_service_boilerplate.__main__ import alchemy, app
from python_web_service_boilerplate.common.common_function import PROJECT_ROOT_PATH, get_module_name
from python_web_service_boilerplate.core.auth.schemas import UserRegistration
from python_web_service_boilerplate.core.auth.service import UserService


@pytest_asyncio.fixture(scope="session")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a database session for testing."""
    async with alchemy.with_async_session() as session:
        yield session


@pytest_asyncio.fixture(scope="session")
async def db_transaction(db_session: AsyncSession) -> AsyncGenerator[AsyncSession, None]:
    """Create a transactional session that rolls back after each test."""
    async with db_session.begin() as transaction:
        yield db_session
        await transaction.rollback()


@pytest_asyncio.fixture(scope="session")
async def user_service(db_transaction: AsyncSession) -> UserService:
    """Create a UserService instance with a test database session."""
    return UserService(session=db_transaction)


@pytest.hookimpl(optionalhook=True)
@pytest_asyncio.fixture(scope="session")
async def pytest_user(user_service: UserService) -> UserRegistration:
    pswd = "pytest"
    user_registration = UserRegistration(
        username="pytest_user",
        password=pswd,
        email="pytest@test.com",
        full_name="pytest user",
        scopes=["admin"],
    )
    try:
        await user_service.create_user(user_registration)
    except Exception as e:
        logger.warning(f"Failed to create user, {e}")
    else:
        logger.info(f"Username '{user_registration.username}' already exists, skipping creation")
    return user_registration


@pytest.fixture(scope="session")
def test_client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


@pytest_asyncio.fixture(scope="session")
async def async_client(test_client: TestClient) -> AsyncGenerator[AsyncClient, None]:
    """Fixture that provides an AsyncClient for testing FastAPI endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=test_client.base_url) as async_client:
        yield async_client


@pytest.hookimpl(optionalhook=True)
@pytest.fixture(scope="session")
def pytest_user_token(pytest_user: UserRegistration, test_client: TestClient) -> TokenResponse:
    response = test_client.post("/api/v1/token", auth=(pytest_user.username, pytest_user.password))
    return TokenResponse.model_validate(response.json())


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
