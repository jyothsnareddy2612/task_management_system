from functools import lru_cache

from src.config.settings import Settings


@lru_cache
def get_auth_settings() -> Settings:
    """Load settings for the standalone auth microservice."""

    return Settings(_env_file="auth/.env")
