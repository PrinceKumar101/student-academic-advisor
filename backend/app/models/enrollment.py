from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.assessment import Assessment
    from app.models.attendance import AttendanceRecord
    from app.models.student import Student
    from app.models.subject import Subject


class Enrollment(Base):
    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint(
            "student_id", "subject_id", name="uq_enrollments_student_subject"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id"), index=True, nullable=False
    )
    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subjects.id", ondelete="RESTRICT"), index=True, nullable=False
    )

    student: Mapped["Student"] = relationship(back_populates="enrollments")
    subject: Mapped["Subject"] = relationship(back_populates="enrollments")
    attendance_records: Mapped[list["AttendanceRecord"]] = relationship(
        back_populates="enrollment",
        cascade="all, delete-orphan",
    )
    assessments: Mapped[list["Assessment"]] = relationship(
        back_populates="enrollment",
        cascade="all, delete-orphan",
    )
