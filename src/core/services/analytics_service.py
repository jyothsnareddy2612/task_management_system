from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.models.postgres.task import Task


class AnalyticsService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def task_counts_by_status(self) -> dict[str, int]:
        result = await self.session.execute(select(Task.status, func.count(Task.id)).group_by(Task.status))
        return {str(status): count for status, count in result.all()}

