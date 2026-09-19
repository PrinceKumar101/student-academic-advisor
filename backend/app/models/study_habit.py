from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.student import Student


def _utc_now() -> datetime:
    return datetime.now(UTC)


class StudyHabit(Base):
    __tablename__ = "study_habits"
    __table_args__ = (
        CheckConstraint(
            "study_hours_per_day >= 0 AND study_hours_per_day <= 24",
            name="ck_study_habits_study_hours",
        ),
        CheckConstraint(
            "self_confidence >= 1 AND self_confidence <= 5",
            name="ck_study_habits_self_confidence",
        ),
        CheckConstraint(
            "available_hours_per_day >= 0 AND available_hours_per_day <= 24",
            name="ck_study_habits_available_hours",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id"), unique=True, nullable=False
    )
    study_hours_per_day: Mapped[float] = mapped_column(Float, nullable=False)
    self_confidence: Mapped[int] = mapped_column(Integer, nullable=False)
    available_hours_per_day: Mapped[float] = mapped_column(Float, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utc_now, onupdate=_utc_now
    )

    student: Mapped["Student"] = relationship(back_populates="study_habit")
