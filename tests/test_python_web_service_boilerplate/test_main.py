from starlette.testclient import TestClient


def test_root(test_client: TestClient) -> None:
    response = test_client.get("/")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
