from datetime import UTC, date, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    JSON,
    Boolean,
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
from app.models.enums import RiskLevel

if TYPE_CHECKING:
    from app.models.student import Student


def _utc_now() -> datetime:
    return datetime.now(UTC)


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"
    __table_args__ = (
        Index(
            "ix_risk_assessments_student_computed_at",
            "student_id",
            "computed_at",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id"), nullable=False
    )
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utc_now
    )
    as_of: Mapped[date] = mapped_column(Date, nullable=False)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    level: Mapped[RiskLevel] = mapped_column(
        Enum(
            RiskLevel,
            native_enum=False,
            length=20,
            values_callable=lambda members: [item.value for item in members],
        ),
        nullable=False,
    )
    escalated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    escalation_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    data_completeness: Mapped[float] = mapped_column(Float, nullable=False)
    config_version: Mapped[str] = mapped_column(String(64), nullable=False)
    components: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    flags: Mapped[list[Any]] = mapped_column(JSON, nullable=False)

    student: Mapped["Student"] = relationship(back_populates="risk_assessments")
