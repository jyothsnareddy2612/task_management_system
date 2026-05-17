from src.handlers.http_clients.base_http_client import BaseHttpClient


class SlackClient(BaseHttpClient):
    async def send_task_notification(self, channel: str, text: str, token: str) -> None:
        await self.request(
            "POST",
            "/api/chat.postMessage",
            json={"channel": channel, "text": text},
            headers={"Authorization": f"Bearer {token}"},
        )

