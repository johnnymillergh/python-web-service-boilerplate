from fastapi_cloud_cli.commands.login import TokenResponse
from loguru import logger
from starlette.testclient import TestClient


def test_hello(test_client: TestClient) -> None:
    response = test_client.get("/hello")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_hello_with_token(test_client: TestClient, pytest_user_token: TokenResponse) -> None:
    response = test_client.get("/hello", headers={"Authorization": f"Bearer {pytest_user_token.access_token}"})
    logger.info(f"Hello response: {response}, {response.json()}")
    assert response.status_code == 200
