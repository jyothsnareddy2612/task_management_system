from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from src.api.rest.dependencies import get_notification_service
from src.core.services.notification_service import NotificationService

router = APIRouter(tags=["realtime"])


@router.websocket("/ws/tasks")
async def task_updates_ws(
    websocket: WebSocket,
    notifications: NotificationService = Depends(get_notification_service),
) -> None:
    await websocket.accept()
    try:
        async for event in notifications.stream():
            await websocket.send_text(event)
    except WebSocketDisconnect:
        return

