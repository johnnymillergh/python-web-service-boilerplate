from faker import Faker
from loguru import logger
from starlette.testclient import TestClient

from python_web_service_boilerplate.system.auth.schemas import UserRegistration


def test_user_registration(test_client: TestClient) -> None:
    faker = Faker()
    first_name = faker.first_name()
    last_name = faker.last_name()
    user_registration = UserRegistration(
        username=f"{first_name.lower()}.{last_name.lower()}",
        password=f"{faker.password()}",
        email=faker.email(),
        full_name=f"{first_name} {last_name}",
    )
    response = test_client.post(url="/api/v1/users", json=user_registration.model_dump())
    response_json = response.json()
    logger.info(f"User registration response: {response}")
    assert response.status_code == 200
    assert set(response_json.keys()) == user_registration.model_dump().keys()
