from __future__ import annotations

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
    assert response.status_code == 200
    assert set(response_json.keys()) == user_registration.model_dump().keys()


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
    assert token_response.status_code == 200
    assert AuthTokenResponse.model_fields.keys() == token_response_json.keys()
