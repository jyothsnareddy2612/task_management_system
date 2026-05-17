from motor.motor_asyncio import AsyncIOMotorClient

from src.config.settings import get_settings


_mongo: AsyncIOMotorClient | None = None


def get_mongo() -> AsyncIOMotorClient:
    """Return a lazy MongoDB client for optional event/log storage."""

    global _mongo
    if _mongo is None:
        _mongo = AsyncIOMotorClient(get_settings().mongo_url)
    return _mongo

