from datetime import UTC, date, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import Priority, Source

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.subject import Subject
    from app.models.user import User


def _utc_now() -> datetime:
    return datetime.now(UTC)


class StudyPlan(Base):
    __tablename__ = "study_plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id"), nullable=False
    )
    exam_date: Mapped[date] = mapped_column(Date, nullable=False)
    available_hours_per_day: Mapped[float] = mapped_column(nullable=False)
    inputs: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
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

    student: Mapped["Student"] = relationship(back_populates="study_plans")
    created_by: Mapped["User"] = relationship()
    items: Mapped[list["StudyPlanItem"]] = relationship(
        back_populates="plan",
        cascade="all, delete-orphan",
    )


class StudyPlanItem(Base):
    __tablename__ = "study_plan_items"
    __table_args__ = (
        CheckConstraint(
            "duration_minutes >= 1 AND duration_minutes <= 480",
            name="ck_study_plan_items_duration",
        ),
        Index("ix_study_plan_items_plan_date", "plan_id", "plan_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    plan_id: Mapped[int] = mapped_column(
        ForeignKey("study_plans.id", ondelete="CASCADE"), nullable=False
    )
    plan_date: Mapped[date] = mapped_column(Date, nullable=False)
    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subjects.id"), nullable=False
    )
    topic: Mapped[str] = mapped_column(String(80), nullable=False)
    activity: Mapped[str] = mapped_column(String(200), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    priority: Mapped[Priority] = mapped_column(
        Enum(
            Priority,
            native_enum=False,
            length=20,
            values_callable=lambda members: [item.value for item in members],
        ),
        nullable=False,
    )
    is_completed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    plan: Mapped[StudyPlan] = relationship(back_populates="items")
    subject: Mapped["Subject"] = relationship(back_populates="study_plan_items")
