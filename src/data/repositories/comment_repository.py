from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.models.postgres.comment import Comment


class CommentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, comment: Comment) -> Comment:
        self.session.add(comment)
        await self.session.flush()
        return comment

    async def list_for_task(self, task_id: UUID) -> list[Comment]:
        result = await self.session.execute(
            select(Comment).where(Comment.task_id == task_id).order_by(Comment.created_at.asc())
        )
        return list(result.scalars().all())

