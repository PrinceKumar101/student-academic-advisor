from datetime import date

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.api.deps import authorize_student_access, get_current_user, require_role
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.student import Student
from app.models.user import User
from app.schemas.students import (
    SemesterResultOut,
    SemesterResultUpdate,
    StudentOverviewOut,
    StudentProfileOut,
    StudyHabitOut,
    StudyHabitUpdate,
)
from app.services import overview_service, student_service

router = APIRouter(prefix="/students", tags=["students"])


@router.get("/{student_id}", response_model=StudentProfileOut)
def get_student(
    student: Student = Depends(authorize_student_access),
) -> StudentProfileOut:
    return student_service.get_profile(student)


@router.get("/{student_id}/overview", response_model=StudentOverviewOut)
def get_student_overview(
    student: Student = Depends(authorize_student_access),
    db: Session = Depends(get_db),
    as_of: date | None = Query(default=None),
) -> StudentOverviewOut:
    return overview_service.get_overview(db, student, as_of or date.today())


@router.get("/{student_id}/study-habits", response_model=StudyHabitOut)
def get_study_habits(
    student: Student = Depends(authorize_student_access),
    db: Session = Depends(get_db),
) -> StudyHabitOut:
    return student_service.get_study_habits(db, student)


@router.put("/{student_id}/study-habits", response_model=StudyHabitOut)
def put_study_habits(
    body: StudyHabitUpdate,
    student: Student = Depends(authorize_student_access),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StudyHabitOut:
    return student_service.upsert_study_habits(db, current_user, student, body)


@router.get("/{student_id}/semester-results", response_model=list[SemesterResultOut])
def get_semester_results(
    student: Student = Depends(authorize_student_access),
    db: Session = Depends(get_db),
) -> list[SemesterResultOut]:
    return student_service.list_semester_results(db, student)


@router.put(
    "/{student_id}/semester-results/{semester}",
    response_model=SemesterResultOut,
)
def put_semester_result(
    body: SemesterResultUpdate,
    semester: int = Path(ge=1, le=8),
    student: Student = Depends(authorize_student_access),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.TEACHER)),
) -> SemesterResultOut:
    return student_service.upsert_semester_result(
        db, current_user, student, semester, body
    )
