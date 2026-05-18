from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "steward-bct-agent"


def test_root_lists_available_endpoints() -> None:
    response = client.get("/")

    assert response.status_code == 200
    payload = response.json()
    assert "Task A" in payload["tasks"]["task_a"]
    assert "/api/task-a/simulate-review" in payload["endpoints"]
