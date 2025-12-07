from collections.abc import Generator
from typing import Any

import pytest
import pytest_asyncio
from fastapi_cloud_cli.commands.login import TokenResponse
from loguru import logger
from starlette.testclient import TestClient

from python_web_service_boilerplate.__main__ import app
from python_web_service_boilerplate.common.common_function import get_module_name
from python_web_service_boilerplate.core.auth.schemas import UserRegistration
from python_web_service_boilerplate.core.auth.service import create_user


@pytest.hookimpl(optionalhook=True)
@pytest_asyncio.fixture(scope="session")
async def pytest_user() -> UserRegistration:
    pswd = "pytest"
    user_registration = UserRegistration(
        username="pytest_user",
        password=pswd,
        email="pytest@test.com",
        full_name="pytest user",
        scopes=["admin"],
    )
    try:
        await create_user(user_registration)
    except Exception as e:
        logger.warning(f"Failed to create user, {e}")
    else:
        logger.info(f"Username '{user_registration.username}' already exists, skipping creation")
    return user_registration


@pytest.fixture(scope="session")
def test_client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


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
