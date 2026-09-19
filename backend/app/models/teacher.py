from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.user import User

if TYPE_CHECKING:
    from app.models.intervention import Intervention
    from app.models.teaching_assignment import TeachingAssignment


class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), unique=True, nullable=False
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    department: Mapped[str] = mapped_column(String(128), nullable=False)

    user: Mapped[User] = relationship(back_populates="teacher")
    teaching_assignments: Mapped[list["TeachingAssignment"]] = relationship(
        back_populates="teacher"
    )
    interventions: Mapped[list["Intervention"]] = relationship(
        back_populates="teacher"
    )
