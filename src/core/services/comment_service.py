from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.constants.enums import UserRole
from src.core.exceptions import NotFoundError, PermissionDeniedError
from src.core.services.notification_service import NotificationService
from src.data.models.postgres.comment import Comment
from src.data.models.postgres.user import User
from src.data.repositories.comment_repository import CommentRepository
from src.data.repositories.task_repository import TaskRepository
from src.schemas.comments import CommentCreate, CommentRead


class CommentService:
    def __init__(self, session: AsyncSession, notifications: NotificationService) -> None:
        self.session = session
        self.comments = CommentRepository(session)
        self.tasks = TaskRepository(session)
        self.notifications = notifications

    async def add(self, task_id: UUID, payload: CommentCreate, actor: User) -> Comment:
        task = await self.tasks.get(task_id)
        if task is None:
            raise NotFoundError("Task not found")
        if actor.role == UserRole.WORKER and task.assigned_to != actor.id:
            raise PermissionDeniedError("Workers can comment only on assigned tasks")
        comment = Comment(task_id=task_id, user_id=actor.id, content=payload.content)
        await self.comments.create(comment)
        await self.session.commit()
        await self.notifications.publish_task_event(
            task_id,
            "comment.created",
            CommentRead.model_validate(comment).model_dump(mode="json"),
        )
        return comment

    async def list_for_task(self, task_id: UUID, actor: User) -> list[Comment]:
        task = await self.tasks.get(task_id)
        if task is None:
            raise NotFoundError("Task not found")
        if actor.role == UserRole.WORKER and task.assigned_to != actor.id:
            raise PermissionDeniedError("Workers can view comments only for assigned tasks")
        return await self.comments.list_for_task(task_id)

