from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.enrollment import Enrollment
    from app.models.intervention import Intervention
    from app.models.study_plan import StudyPlanItem
    from app.models.teaching_assignment import TeachingAssignment


class Subject(Base):
    __tablename__ = "subjects"
    __table_args__ = (
        CheckConstraint(
            "semester >= 1 AND semester <= 8", name="ck_subjects_semester"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    semester: Mapped[int] = mapped_column(Integer, nullable=False)

    enrollments: Mapped[list["Enrollment"]] = relationship(
        back_populates="subject",
        passive_deletes="all",
    )
    teaching_assignments: Mapped[list["TeachingAssignment"]] = relationship(
        back_populates="subject"
    )
    study_plan_items: Mapped[list["StudyPlanItem"]] = relationship(
        back_populates="subject"
    )
    interventions: Mapped[list["Intervention"]] = relationship(
        back_populates="subject"
    )
