from faker import Faker
from loguru import logger
from starlette.testclient import TestClient


def test_root(test_client: TestClient) -> None:
    faker = Faker()
    first_name = faker.first_name()
    last_name = faker.last_name()
    response = test_client.post(
        url="/api/v1/users",
        json={
            "username": f"{first_name.lower()}.{last_name.lower()}",
            "password": "123456",
            "email": f"{faker.email()}",
            "full_name": f"{first_name} {last_name}",
        },
    )
    response_json = response.json()
    logger.info(f"Response: {response_json}")
    assert response.status_code == 200
    expected_keys = {"username", "password", "email", "full_name"}
    assert set(response_json.keys()) == expected_keys
