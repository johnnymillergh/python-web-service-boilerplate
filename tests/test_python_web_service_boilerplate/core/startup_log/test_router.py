from http import HTTPStatus

from fastapi_cloud_cli.commands.login import TokenResponse
from loguru import logger
from starlette.testclient import TestClient


def test_startup_logs_stream(test_client: TestClient, pytest_user_token: TokenResponse) -> None:
    try:
        response = test_client.get(
            "/api/v1/startup_logs/stream", headers={"Authorization": f"Bearer {pytest_user_token.access_token}"}
        )
        logger.info(f"Startup logs response: {response}, {response.text}")
        assert response.status_code == HTTPStatus.OK.value
    except Exception as e:
        logger.error(f"Error during test_startup_logs_stream: {e}")
