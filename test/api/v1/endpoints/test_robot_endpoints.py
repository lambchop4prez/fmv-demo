from fastapi.testclient import TestClient

from api import app

client = TestClient(app)

ENDPOINT = "/api/v1/robot"


def test_get_robots_is_successful() -> None:
    response = client.get(ENDPOINT)
    assert response.status_code == 200


def test_get_robot() -> None:
    response = client.get(f"{ENDPOINT}/Bender")

    assert response.status_code == 200
    assert response.json()["name"] == "Bender"


def test_get_robot_unknown_item() -> None:
    response = client.get(f"{ENDPOINT}/unknown")

    assert response.status_code == 404
