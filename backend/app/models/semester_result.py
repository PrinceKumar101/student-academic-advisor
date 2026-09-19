from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.student import Student


class SemesterResult(Base):
    __tablename__ = "semester_results"
    __table_args__ = (
        UniqueConstraint(
            "student_id", "semester", name="uq_semester_results_student_semester"
        ),
        CheckConstraint(
            "semester >= 1 AND semester <= 8", name="ck_semester_results_semester"
        ),
        CheckConstraint(
            "percentage >= 0 AND percentage <= 100",
            name="ck_semester_results_percentage",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    semester: Mapped[int] = mapped_column(Integer, nullable=False)
    percentage: Mapped[float] = mapped_column(Float, nullable=False)
    sgpa: Mapped[float | None] = mapped_column(Float, nullable=True)

    student: Mapped["Student"] = relationship(back_populates="semester_results")
