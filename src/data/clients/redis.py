from redis.asyncio import Redis

from src.config.settings import get_settings


_redis: Redis | None = None


async def get_redis() -> Redis:
    """Return a shared Redis client for cache and pub/sub operations."""

    global _redis
    if _redis is None:
        _redis = Redis.from_url(
            get_settings().redis_url,
            decode_responses=True,
            socket_connect_timeout=1,
            socket_timeout=1,
        )
    return _redis


async def close_redis() -> None:
    if _redis is not None:
        await _redis.aclose()
