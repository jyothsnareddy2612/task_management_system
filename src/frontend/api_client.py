from dataclasses import dataclass
from typing import Any

import requests


@dataclass
class ApiClient:
    base_url: str
    token: str = ""

    @property
    def headers(self) -> dict[str, str]:
        if not self.token:
            return {}
        return {"Authorization": f"Bearer {self.token}"}

    def request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        headers = dict(self.headers)
        headers.update(kwargs.pop("headers", {}))
        return requests.request(
            method,
            f"{self.base_url}{path}",
            headers=headers,
            timeout=10,
            **kwargs,
        )

    def me(self) -> requests.Response:
        return self.request("GET", "/auth/me")

    def list_users(self) -> requests.Response:
        return self.request("GET", "/admin/users")

    def list_tasks(self, status: str | None = None) -> requests.Response:
        params = {} if status in (None, "ALL") else {"status": status}
        return self.request("GET", "/tasks", params=params)

    def create_task(self, payload: dict[str, Any]) -> requests.Response:
        return self.request("POST", "/tasks", json=payload)

    def update_task(self, task_id: str, payload: dict[str, Any]) -> requests.Response:
        return self.request("PATCH", f"/tasks/{task_id}", json=payload)

    def delete_task(self, task_id: str) -> requests.Response:
        return self.request("DELETE", f"/tasks/{task_id}")

    def list_comments(self, task_id: str) -> requests.Response:
        return self.request("GET", f"/tasks/{task_id}/comments")

    def add_comment(self, task_id: str, content: str) -> requests.Response:
        return self.request("POST", f"/tasks/{task_id}/comments", json={"content": content})

    def task_history(self, task_id: str) -> requests.Response:
        return self.request("GET", f"/tasks/{task_id}/history")

    def task_analytics(self) -> requests.Response:
        return self.request("GET", "/admin/analytics/tasks")

