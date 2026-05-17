from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse

from src.api.rest.dependencies import get_current_user, get_notification_service
from src.core.services.notification_service import NotificationService
from src.data.models.postgres.user import User

router = APIRouter(prefix="/events", tags=["realtime"])


@router.get("/tasks")
async def task_events(
    _: User = Depends(get_current_user),
    notifications: NotificationService = Depends(get_notification_service),
) -> EventSourceResponse:
    async def event_generator() -> object:
        async for event in notifications.stream():
            yield {"event": "task-update", "data": event}

    return EventSourceResponse(event_generator())

