from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import ChatMessageRole, Source

if TYPE_CHECKING:
    from app.models.student import Student


def _utc_now() -> datetime:
    return datetime.now(UTC)


class AIChatMessage(Base):
    __tablename__ = "ai_chat_messages"
    __table_args__ = (
        Index("ix_ai_chat_messages_student_created", "student_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id"), nullable=False
    )
    role: Mapped[ChatMessageRole] = mapped_column(
        Enum(
            ChatMessageRole,
            native_enum=False,
            length=20,
            values_callable=lambda members: [item.value for item in members],
        ),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[Source | None] = mapped_column(
        Enum(
            Source,
            native_enum=False,
            length=20,
            values_callable=lambda members: [item.value for item in members],
        ),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utc_now
    )

    student: Mapped["Student"] = relationship(back_populates="chat_messages")
