from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.data.models.postgres.task_history import TaskHistory


class HistoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, history: TaskHistory) -> TaskHistory:
        self.session.add(history)
        await self.session.flush()
        return history

    async def list_for_task(self, task_id: object) -> list[TaskHistory]:
        result = await self.session.execute(
            select(TaskHistory)
            .where(TaskHistory.task_id == task_id)
            .order_by(TaskHistory.changed_at.desc())
        )
        return list(result.scalars().all())
