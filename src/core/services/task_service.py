from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.constants.enums import TaskStatus, UserRole
from src.core.exceptions import NotFoundError, PermissionDeniedError
from src.core.services.notification_service import NotificationService
from src.data.models.postgres.task import Task
from src.data.models.postgres.task_history import TaskHistory
from src.data.models.postgres.user import User
from src.data.repositories.history_repository import HistoryRepository
from src.data.repositories.task_repository import TaskRepository
from src.schemas.tasks import TaskCreate, TaskHistoryRead, TaskPage, TaskRead, TaskUpdate


class TaskService:
    def __init__(self, session: AsyncSession, notifications: NotificationService) -> None:
        self.session = session
        self.tasks = TaskRepository(session)
        self.history = HistoryRepository(session)
        self.notifications = notifications

    async def create(self, payload: TaskCreate, actor: User) -> Task:
        self._require_admin(actor)
        task = Task(**payload.model_dump(), created_by=actor.id)
        await self.tasks.create(task)
        await self.session.commit()
        await self.notifications.publish_task_event(task.id, "task.created", TaskRead.model_validate(task).model_dump(mode="json"))
        return task

    async def list(
        self,
        *,
        actor: User,
        limit: int,
        offset: int,
        assigned_to: UUID | None,
        status: TaskStatus | None,
    ) -> TaskPage:
        effective_assignee = assigned_to
        if actor.role == UserRole.WORKER:
            effective_assignee = actor.id
        tasks, total = await self.tasks.list(
            limit=limit,
            offset=offset,
            assigned_to=effective_assignee,
            status=status,
        )
        return TaskPage(
            items=[TaskRead.model_validate(task) for task in tasks],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def update(self, task_id: UUID, payload: TaskUpdate, actor: User) -> Task:
        task = await self.tasks.get(task_id)
        if task is None:
            raise NotFoundError("Task not found")
        if actor.role == UserRole.WORKER and task.assigned_to != actor.id:
            raise PermissionDeniedError("Workers can update only assigned tasks")

        old_status = task.status
        update_data = payload.model_dump(exclude_unset=True)
        if actor.role == UserRole.WORKER:
            update_data = {"status": update_data.get("status")} if "status" in update_data else {}
        new_status = update_data.get("status")
        if isinstance(new_status, TaskStatus):
            self._validate_status_transition(old_status, new_status)
        for field, value in update_data.items():
            setattr(task, field, value)

        if payload.status is not None and payload.status != old_status:
            await self.history.create(
                TaskHistory(
                    task_id=task.id,
                    old_status=old_status,
                    new_status=payload.status,
                    changed_by=actor.id,
                )
            )
        await self.session.commit()
        await self.notifications.publish_task_event(task.id, "task.updated", TaskRead.model_validate(task).model_dump(mode="json"))
        return task

    async def delete(self, task_id: UUID, actor: User) -> None:
        self._require_admin(actor)
        task = await self.tasks.get(task_id)
        if task is None:
            raise NotFoundError("Task not found")
        await self.tasks.delete(task)
        await self.session.commit()
        await self.notifications.publish_task_event(task_id, "task.deleted", {"id": str(task_id)})

    async def history_for_task(self, task_id: UUID, actor: User) -> list[TaskHistoryRead]:
        task = await self.tasks.get(task_id)
        if task is None:
            raise NotFoundError("Task not found")
        if actor.role == UserRole.WORKER and task.assigned_to != actor.id:
            raise PermissionDeniedError("Workers can view history only for assigned tasks")
        history = await self.history.list_for_task(task_id)
        return [TaskHistoryRead.model_validate(item) for item in history]

    def _require_admin(self, actor: User) -> None:
        if actor.role != UserRole.ADMIN:
            raise PermissionDeniedError("Admin role required")

    def _validate_status_transition(self, old_status: TaskStatus, new_status: TaskStatus) -> None:
        allowed_transitions = {
            TaskStatus.TODO: {TaskStatus.TODO, TaskStatus.IN_PROGRESS},
            TaskStatus.IN_PROGRESS: {TaskStatus.IN_PROGRESS, TaskStatus.DONE},
            TaskStatus.DONE: {TaskStatus.DONE},
        }
        if new_status not in allowed_transitions[old_status]:
            raise PermissionDeniedError(
                f"Invalid status transition: {old_status} cannot move to {new_status}"
            )
