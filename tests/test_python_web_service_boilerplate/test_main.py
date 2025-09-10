from http import HTTPStatus

from fastapi_cloud_cli.commands.login import TokenResponse
from loguru import logger
from starlette.testclient import TestClient


def test_hello(test_client: TestClient) -> None:
    response = test_client.get("/hello")
    assert response.status_code == HTTPStatus.UNAUTHORIZED.value
    assert response.json() == {"detail": "Not authenticated"}


def test_hello_with_token(test_client: TestClient, pytest_user_token: TokenResponse) -> None:
    response = test_client.get("/hello", headers={"Authorization": f"Bearer {pytest_user_token.access_token}"})
    logger.info(f"Hello response: {response}, {response.json()}")
    assert response.status_code == HTTPStatus.OK.value


def test_hello_with_invalid_token_without_sub(test_client: TestClient, pytest_user_token: TokenResponse) -> None:
    """
    {
        "sub": null,
        "expires_at": "2025-08-24T09:44:26.796899"
    }
    Invalid token generated from above payload.
    """
    response = test_client.get(
        "/hello",
        headers={
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOm51bGwsImV4cGlyZXNfYXQiOiIyMDI1"
            "LTA4LTI0VDA5OjQ0OjI2Ljc5Njg5OSJ9.ARw1mW3KnjWxNHJIWsMpg4cEzyqUCQAP_mVVY-x1if4"
        },
    )
    logger.info(f"Hello response: {response}, {response.json()}")
    assert response.status_code == HTTPStatus.UNAUTHORIZED.value
    assert "Invalid token: Subject must be a string." in response.text


def test_hello_with_invalid_token_with_expired_date(test_client: TestClient, pytest_user_token: TokenResponse) -> None:
    """
    {
        "sub": "pytest_user",
        "expires_at": "2025-08-24T09:44:26.796899"
    }
    Invalid token generated from above payload.
    """
    response = test_client.get(
        "/hello",
        headers={
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwiZWF0IjoiMjAyNS0w"
            "OC0yNFQwOTo0NDoyNi43OTY4OTkiLCJzY3AiOiJ1c2VyOnJlYWQifQ.XcFLkk3Kvr-5Mdso-l7aDfw-swFqzqlOvjF6zMNK85Q"
        },
    )
    logger.info(f"Hello response: {response}, {response.json()}")
    assert response.status_code == HTTPStatus.UNAUTHORIZED.value
    assert "Invalid token: expired" in response.text
