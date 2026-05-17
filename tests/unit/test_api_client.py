import requests

from src.frontend.api_client import ApiClient


def test_api_client_attaches_bearer_token(monkeypatch: object) -> None:
    captured: dict[str, object] = {}

    def fake_request(method: str, url: str, **kwargs: object) -> requests.Response:
        captured["method"] = method
        captured["url"] = url
        captured["headers"] = kwargs["headers"]
        response = requests.Response()
        response.status_code = 200
        return response

    monkeypatch.setattr(requests, "request", fake_request)  # type: ignore[attr-defined]

    ApiClient("http://localhost:8000/api/v1", "token").list_tasks("TODO")

    assert captured["method"] == "GET"
    assert captured["url"] == "http://localhost:8000/api/v1/tasks"
    assert captured["headers"] == {"Authorization": "Bearer token"}

