from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.data.clients.postgres import Base
from src.data.models.postgres.base import UUIDPrimaryKeyMixin, utc_now


class Comment(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "comments"

    task_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("tasks.id"), index=True)
    user_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("users.id"), index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at = mapped_column(DateTime(timezone=True), default=utc_now)

    task = relationship("Task", back_populates="comments")

