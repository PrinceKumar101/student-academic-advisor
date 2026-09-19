from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import AdviceKind, Source

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.user import User


def _utc_now() -> datetime:
    return datetime.now(UTC)


class AIAdvice(Base):
    __tablename__ = "ai_advice"
    __table_args__ = (
        Index(
            "ix_ai_advice_student_kind_hash",
            "student_id",
            "kind",
            "input_hash",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id"), nullable=False
    )
    kind: Mapped[AdviceKind] = mapped_column(
        Enum(
            AdviceKind,
            native_enum=False,
            length=20,
            values_callable=lambda members: [item.value for item in members],
        ),
        nullable=False,
    )
    input_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    source: Mapped[Source] = mapped_column(
        Enum(
            Source,
            native_enum=False,
            length=20,
            values_callable=lambda members: [item.value for item in members],
        ),
        nullable=False,
    )
    model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    prompt_version: Mapped[str] = mapped_column(String(64), nullable=False)
    created_by_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utc_now
    )

    student: Mapped["Student"] = relationship(back_populates="ai_advice")
    created_by: Mapped["User"] = relationship()
