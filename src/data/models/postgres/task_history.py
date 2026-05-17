from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.constants.enums import TaskStatus
from src.data.clients.postgres import Base
from src.data.models.postgres.base import UUIDPrimaryKeyMixin, utc_now


class TaskHistory(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "task_history"

    task_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("tasks.id"), index=True)
    old_status: Mapped[TaskStatus | None] = mapped_column(String(30))
    new_status: Mapped[TaskStatus] = mapped_column(String(30), nullable=False)
    changed_by: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("users.id"))
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    task = relationship("Task", back_populates="history")

