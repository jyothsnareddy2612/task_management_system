from datetime import datetime, timezone
from typing import Any

import structlog

from src.data.clients.mongo import get_mongo

logger = structlog.get_logger(__name__)


class EventLogService:
    """Optional MongoDB-backed event log for NoSQL/Motor demonstrations."""

    def __init__(self, database_name: str = "task_management") -> None:
        self.database_name = database_name

    async def record_event(self, event_type: str, payload: dict[str, Any]) -> None:
        try:
            mongo = get_mongo()
            await mongo[self.database_name]["events"].insert_one(
                {
                    "event_type": event_type,
                    "payload": payload,
                    "created_at": datetime.now(timezone.utc),
                }
            )
        except Exception as exc:
            logger.warning("mongo_event_log_skipped", event_type=event_type, error=str(exc))
