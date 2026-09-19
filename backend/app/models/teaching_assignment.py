from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.subject import Subject
    from app.models.teacher import Teacher


class TeachingAssignment(Base):
    __tablename__ = "teaching_assignments"
    __table_args__ = (
        UniqueConstraint(
            "teacher_id",
            "subject_id",
            "section",
            name="uq_teaching_assignments_teacher_subject_section",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id"), nullable=False)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), nullable=False)
    section: Mapped[str] = mapped_column(
        String(16), nullable=False, default="ALL", server_default=text("'ALL'")
    )

    teacher: Mapped["Teacher"] = relationship(back_populates="teaching_assignments")
    subject: Mapped["Subject"] = relationship(back_populates="teaching_assignments")
