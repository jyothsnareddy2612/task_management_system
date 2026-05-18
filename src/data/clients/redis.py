from redis.asyncio import Redis

from src.config.settings import get_settings


_redis: Redis | None = None
#Global singleton client.



async def get_redis() -> Redis:
    """Return a shared Redis client for cache and pub/sub operations."""

    global _redis
    if _redis is None:
        _redis = Redis.from_url(
            get_settings().redis_url,
            decode_responses=True, #redis normally returns bytes,decode_responses=True makes it return strings
            socket_connect_timeout=1,
            socket_timeout=1, #failure fast architecture:fail quickly and recover gracefully
        )
    return _redis


async def close_redis() -> None:
    if _redis is not None:
        await _redis.aclose()
