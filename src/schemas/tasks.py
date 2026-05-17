from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.constants.enums import TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    assigned_to: UUID | None = None
    due_date: datetime | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=200)
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    assigned_to: UUID | None = None
    due_date: datetime | None = None


class TaskRead(BaseModel):
    id: UUID
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    assigned_to: UUID | None
    created_by: UUID
    due_date: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskPage(BaseModel):
    items: list[TaskRead]
    total: int
    limit: int
    offset: int


class TaskHistoryRead(BaseModel):
    id: UUID
    task_id: UUID
    old_status: TaskStatus | None
    new_status: TaskStatus
    changed_by: UUID
    changed_at: datetime

    model_config = {"from_attributes": True}
