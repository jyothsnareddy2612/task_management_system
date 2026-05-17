import json
import logging
from collections.abc import AsyncGenerator
from uuid import UUID

from redis.exceptions import RedisError

from src.data.clients.redis import get_redis

logger = logging.getLogger(__name__)


class NotificationService:
    """Publishes realtime task events to Redis for WebSocket/SSE fanout."""

    channel = "task-events"

    async def publish_task_event(self, task_id: UUID, event_type: str, payload: dict[str, object]) -> None:
        try:
            redis = await get_redis()
            await redis.publish(
                self.channel,
                json.dumps({"task_id": str(task_id), "event_type": event_type, "payload": payload}),
            )
        except RedisError:
            logger.warning("Realtime publish skipped because Redis is unavailable", exc_info=True)

    async def stream(self) -> AsyncGenerator[str, None]:
        try:
            redis = await get_redis()
            pubsub = redis.pubsub()
            await pubsub.subscribe(self.channel)
        except RedisError:
            logger.warning("Realtime stream unavailable because Redis is unavailable", exc_info=True)
            return
        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    yield str(message["data"])
        finally:
            await pubsub.unsubscribe(self.channel)
            await pubsub.close()
