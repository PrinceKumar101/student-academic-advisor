from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import Conflict, Forbidden, NotFound
from app.models.enums import UserRole
from app.models.semester_result import SemesterResult
from app.models.student import Student
from app.models.study_habit import StudyHabit
from app.models.user import User
from app.schemas.students import (
    SemesterResultOut,
    SemesterResultUpdate,
    StudentProfileOut,
    StudyHabitOut,
    StudyHabitUpdate,
)


def get_profile(student: Student) -> StudentProfileOut:
    return StudentProfileOut.model_validate(student)


def _habit_for(db: Session, student_id: int) -> StudyHabit | None:
    return db.execute(
        select(StudyHabit).where(StudyHabit.student_id == student_id)
    ).scalar_one_or_none()


def get_study_habits(db: Session, student: Student) -> StudyHabitOut:
    habit = _habit_for(db, student.id)
    if habit is None:
        raise NotFound("Study habits not found")
    return StudyHabitOut.model_validate(habit)


def upsert_study_habits(
    db: Session, current_user: User, student: Student, body: StudyHabitUpdate
) -> StudyHabitOut:
    if current_user.role != UserRole.STUDENT or current_user.student is None:
        raise Forbidden("Only a student can update study habits")
    if current_user.student.id != student.id:
        raise Forbidden("Cannot update another student's study habits")
    habit = _habit_for(db, student.id)
    if habit is None:
        habit = StudyHabit(student_id=student.id, **body.model_dump())
        db.add(habit)
    else:
        habit.study_hours_per_day = body.study_hours_per_day
        habit.self_confidence = body.self_confidence
        habit.available_hours_per_day = body.available_hours_per_day
    db.commit()
    db.refresh(habit)
    return StudyHabitOut.model_validate(habit)


def list_semester_results(db: Session, student: Student) -> list[SemesterResultOut]:
    rows = db.execute(
        select(SemesterResult)
        .where(SemesterResult.student_id == student.id)
        .order_by(SemesterResult.semester)
    ).scalars().all()
    return [SemesterResultOut.model_validate(row) for row in rows]


def upsert_semester_result(
    db: Session,
    current_user: User,
    student: Student,
    semester: int,
    body: SemesterResultUpdate,
) -> SemesterResultOut:
    if current_user.role != UserRole.TEACHER:
        raise Forbidden("Only a teacher can update semester results")
    row = db.execute(
        select(SemesterResult).where(
            SemesterResult.student_id == student.id,
            SemesterResult.semester == semester,
        )
    ).scalar_one_or_none()
    if row is None:
        row = SemesterResult(
            student_id=student.id,
            semester=semester,
            percentage=body.percentage,
            sgpa=body.sgpa,
        )
        db.add(row)
    else:
        row.percentage = body.percentage
        row.sgpa = body.sgpa
    try:
        db.commit()
        db.refresh(row)
    except IntegrityError as exc:
        db.rollback()
        raise Conflict("Semester result already exists") from exc
    return SemesterResultOut.model_validate(row)
