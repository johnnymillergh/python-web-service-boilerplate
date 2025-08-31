from __future__ import annotations

from http import HTTPStatus

from faker import Faker
from loguru import logger
from starlette.testclient import TestClient

from python_web_service_boilerplate.system.auth.schemas import AuthTokenResponse, UserRegistration

user_registration: UserRegistration | None


def test_user_registration(test_client: TestClient) -> None:
    faker = Faker()
    first_name = faker.first_name()
    last_name = faker.last_name()
    global user_registration
    user_registration = UserRegistration(
        username=f"{first_name.lower()}.{last_name.lower()}",
        password=f"{faker.password()}",
        email=faker.email(),
        full_name=f"{first_name} {last_name}",
    )
    response = test_client.post(url="/api/v1/users", json=user_registration.model_dump())
    response_json = response.json()
    logger.info(f"User registration response: {response}, {response_json}")
    assert response.status_code == HTTPStatus.OK.value
    assert set(response_json.keys()) == user_registration.model_dump().keys()


def test_same_user_registration(test_client: TestClient) -> None:
    response = test_client.post(url="/api/v1/users", json=user_registration.model_dump() if user_registration else {})
    response_json = response.json()
    logger.info(f"User registration response: {response}, {response_json}")
    assert response.status_code == HTTPStatus.BAD_REQUEST.value
    assert "Username already exists" in response.text


def test_user_registration_and_get_token(test_client: TestClient) -> None:
    # Get token using HTTP Basic Auth
    token_response = test_client.post(
        url="/api/v1/token",
        auth=(
            user_registration.username if user_registration else "",
            user_registration.password if user_registration else "",
        ),
    )
    token_response_json = token_response.json()
    logger.info(f"Token response: {token_response}, {token_response_json}")
    assert token_response.status_code == HTTPStatus.OK.value
    assert AuthTokenResponse.model_fields.keys() == token_response_json.keys()


def test_token_when_user_not_found(test_client: TestClient) -> None:
    # Get token using HTTP Basic Auth
    token_response = test_client.post(
        url="/api/v1/token",
        auth=(
            "non_existing_user",
            user_registration.password if user_registration else "",
        ),
    )
    token_response_text = token_response.text
    logger.info(f"Token response: {token_response}, {token_response_text}")
    assert token_response.status_code == HTTPStatus.UNAUTHORIZED.value
    assert "Invalid username or password" in token_response_text


def test_token_when_password_incorrect(test_client: TestClient) -> None:
    # Get token using HTTP Basic Auth
    token_response = test_client.post(
        url="/api/v1/token",
        auth=(
            user_registration.username if user_registration else "",
            "incorrect_pswd",
        ),
    )
    token_response_text = token_response.text
    logger.info(f"Token response: {token_response}, {token_response_text}")
    assert token_response.status_code == HTTPStatus.UNAUTHORIZED.value
    assert "Invalid username or password" in token_response_text
