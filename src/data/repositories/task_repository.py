from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.constants.enums import TaskStatus
from src.data.models.postgres.task import Task


class TaskRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, task_id: UUID) -> Task | None:
        return await self.session.get(Task, task_id)

    async def create(self, task: Task) -> Task:
        self.session.add(task)
        await self.session.flush()
        return task

    async def list(
        self,
        *,
        limit: int,
        offset: int,
        assigned_to: UUID | None = None,
        status: TaskStatus | None = None,
    ) -> tuple[list[Task], int]:
        query: Select[tuple[Task]] = select(Task).order_by(Task.created_at.desc())
        count_query = select(func.count(Task.id))
        if assigned_to is not None:
            query = query.where(Task.assigned_to == assigned_to)
            count_query = count_query.where(Task.assigned_to == assigned_to)
        if status is not None:
            query = query.where(Task.status == status)
            count_query = count_query.where(Task.status == status)

        total = await self.session.scalar(count_query)
        result = await self.session.execute(query.limit(limit).offset(offset))
        return list(result.scalars().all()), int(total or 0)

    async def delete(self, task: Task) -> None:
        await self.session.delete(task)

