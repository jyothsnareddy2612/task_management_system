from src.handlers.http_clients.base_http_client import BaseHttpClient


class EmailClient(BaseHttpClient):
    async def send_email(self, to_email: str, subject: str, body: str) -> None:
        await self.request("POST", "/email/send", json={"to": to_email, "subject": subject, "body": body})

