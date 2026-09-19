from datetime import UTC, date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import AssessmentStatus, AssessmentType

if TYPE_CHECKING:
    from app.models.enrollment import Enrollment


def _utc_now() -> datetime:
    return datetime.now(UTC)


class Assessment(Base):
    __tablename__ = "assessments"
    __table_args__ = (
        CheckConstraint("max_marks > 0", name="ck_assessments_max_marks"),
        CheckConstraint(
            "obtained_marks IS NULL OR "
            "(obtained_marks >= 0 AND obtained_marks <= max_marks)",
            name="ck_assessments_obtained_marks",
        ),
        CheckConstraint(
            "status <> 'GRADED' OR obtained_marks IS NOT NULL",
            name="ck_assessments_graded_has_marks",
        ),
        Index(
            "ix_assessments_enrollment_type_date",
            "enrollment_id",
            "type",
            "assessment_date",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    enrollment_id: Mapped[int] = mapped_column(
        ForeignKey("enrollments.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[AssessmentType] = mapped_column(
        Enum(
            AssessmentType,
            native_enum=False,
            length=20,
            values_callable=lambda members: [item.value for item in members],
        ),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    max_marks: Mapped[float] = mapped_column(Float, nullable=False)
    obtained_marks: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[AssessmentStatus] = mapped_column(
        Enum(
            AssessmentStatus,
            native_enum=False,
            length=20,
            values_callable=lambda members: [item.value for item in members],
        ),
        nullable=False,
    )
    assessment_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utc_now
    )

    enrollment: Mapped["Enrollment"] = relationship(back_populates="assessments")
