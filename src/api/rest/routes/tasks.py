from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.api.rest.dependencies import get_current_user, get_task_service
from src.constants.enums import TaskStatus
from src.core.services.task_service import TaskService
from src.data.models.postgres.user import User
from src.schemas.tasks import TaskCreate, TaskHistoryRead, TaskPage, TaskRead, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: TaskCreate,
    actor: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
) -> object:
    return await service.create(payload, actor)


@router.get("", response_model=TaskPage)
async def list_tasks(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    assigned_to: UUID | None = None,
    task_status: TaskStatus | None = Query(default=None, alias="status"),
    actor: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
) -> TaskPage:
    return await service.list(
        actor=actor,
        limit=limit,
        offset=offset,
        assigned_to=assigned_to,
        status=task_status,
    )


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: UUID,
    payload: TaskUpdate,
    actor: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
) -> object:
    return await service.update(task_id, payload, actor)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    actor: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
) -> None:
    await service.delete(task_id, actor)


@router.get("/{task_id}/history", response_model=list[TaskHistoryRead])
async def task_history(
    task_id: UUID,
    actor: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
) -> list[TaskHistoryRead]:
    return await service.history_for_task(task_id, actor)
