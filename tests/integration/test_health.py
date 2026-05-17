from fastapi.testclient import TestClient

from src.main import app


def test_readiness() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}

