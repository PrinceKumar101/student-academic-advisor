from datetime import UTC, date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import InterventionStatus, Priority, RiskLevel

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.subject import Subject
    from app.models.teacher import Teacher


def _utc_now() -> datetime:
    return datetime.now(UTC)


class Intervention(Base):
    __tablename__ = "interventions"
    __table_args__ = (
        Index("ix_interventions_student_status", "student_id", "status"),
        Index("ix_interventions_teacher_status", "teacher_id", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id"), nullable=False
    )
    teacher_id: Mapped[int] = mapped_column(
        ForeignKey("teachers.id"), nullable=False
    )
    subject_id: Mapped[int | None] = mapped_column(
        ForeignKey("subjects.id"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[Priority] = mapped_column(
        Enum(
            Priority,
            native_enum=False,
            length=20,
            values_callable=lambda members: [item.value for item in members],
        ),
        nullable=False,
        default=Priority.MEDIUM,
    )
    status: Mapped[InterventionStatus] = mapped_column(
        Enum(
            InterventionStatus,
            native_enum=False,
            length=20,
            values_callable=lambda members: [item.value for item in members],
        ),
        nullable=False,
        default=InterventionStatus.PENDING,
    )
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    baseline_score: Mapped[float | None] = mapped_column(nullable=True)
    baseline_level: Mapped[RiskLevel] = mapped_column(
        Enum(
            RiskLevel,
            native_enum=False,
            length=20,
            values_callable=lambda members: [item.value for item in members],
        ),
        nullable=False,
    )
    baseline_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    outcome_score: Mapped[float | None] = mapped_column(nullable=True)
    outcome_level: Mapped[RiskLevel | None] = mapped_column(
        Enum(
            RiskLevel,
            native_enum=False,
            length=20,
            values_callable=lambda members: [item.value for item in members],
        ),
        nullable=True,
    )
    outcome_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completion_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utc_now,
        onupdate=_utc_now,
    )

    student: Mapped["Student"] = relationship(back_populates="interventions")
    teacher: Mapped["Teacher"] = relationship(back_populates="interventions")
    subject: Mapped["Subject | None"] = relationship(
        back_populates="interventions"
    )
