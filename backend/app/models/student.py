from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.user import User

if TYPE_CHECKING:
    from app.models.ai_advice import AIAdvice
    from app.models.ai_chat_message import AIChatMessage
    from app.models.enrollment import Enrollment
    from app.models.intervention import Intervention
    from app.models.risk_assessment import RiskAssessment
    from app.models.semester_result import SemesterResult
    from app.models.study_habit import StudyHabit
    from app.models.study_plan import StudyPlan


def _utc_now() -> datetime:
    return datetime.now(UTC)


class Student(Base):
    __tablename__ = "students"
    __table_args__ = (
        CheckConstraint(
            "semester >= 1 AND semester <= 8", name="ck_students_semester"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), unique=True, nullable=False
    )
    student_code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    department: Mapped[str] = mapped_column(String(128), nullable=False)
    semester: Mapped[int] = mapped_column(Integer, nullable=False)
    section: Mapped[str] = mapped_column(String(16), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utc_now
    )

    user: Mapped[User] = relationship(back_populates="student")
    enrollments: Mapped[list["Enrollment"]] = relationship(back_populates="student")
    semester_results: Mapped[list["SemesterResult"]] = relationship(
        back_populates="student"
    )
    study_habit: Mapped["StudyHabit | None"] = relationship(
        back_populates="student", uselist=False
    )
    risk_assessments: Mapped[list["RiskAssessment"]] = relationship(
        back_populates="student"
    )
    ai_advice: Mapped[list["AIAdvice"]] = relationship(back_populates="student")
    study_plans: Mapped[list["StudyPlan"]] = relationship(back_populates="student")
    chat_messages: Mapped[list["AIChatMessage"]] = relationship(
        back_populates="student"
    )
    interventions: Mapped[list["Intervention"]] = relationship(
        back_populates="student"
    )
