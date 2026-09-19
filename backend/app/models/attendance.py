from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.enrollment import Enrollment


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    __table_args__ = (
        UniqueConstraint(
            "enrollment_id",
            "record_date",
            name="uq_attendance_records_enrollment_date",
        ),
        CheckConstraint("classes_held >= 0", name="ck_attendance_classes_held"),
        CheckConstraint(
            "classes_attended >= 0 AND classes_attended <= classes_held",
            name="ck_attendance_classes_attended",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    enrollment_id: Mapped[int] = mapped_column(
        ForeignKey("enrollments.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    record_date: Mapped[date] = mapped_column(Date, nullable=False)
    classes_held: Mapped[int] = mapped_column(Integer, nullable=False)
    classes_attended: Mapped[int] = mapped_column(Integer, nullable=False)

    enrollment: Mapped["Enrollment"] = relationship(back_populates="attendance_records")
