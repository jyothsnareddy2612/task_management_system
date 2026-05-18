from functools import lru_cache
from typing import Literal

from pydantic import AnyUrl, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Task Management System"
    environment: Literal["local", "dev", "staging", "prod"] = "local"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/task_management"
    redis_url: str = "redis://localhost:6379/0"
    mongo_url: str = "mongodb://localhost:27017"
    jwt_secret_key: SecretStr = Field(default=SecretStr("change-me-in-production"))
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    cors_origins: list[str | AnyUrl] = ["http://localhost:5173"]
    google_oauth_client_id: str | None = None
    google_oauth_client_secret: SecretStr | None = None
    google_oauth_redirect_uri: str = "http://localhost:8001/api/v1/auth/google/callback"
    oauth_success_redirect_url: str | None = "http://localhost:5173"
    google_admin_emails: list[str] = []

    @property
    def is_production(self) -> bool:
        return self.environment == "prod"
#Problem Without Cache

#Every dependency injection call:
#creates new Settings instance.

@lru_cache
def get_settings() -> Settings:
    """Return cached settings to keep dependency injection cheap."""

    return Settings()
