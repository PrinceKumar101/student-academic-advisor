from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from starlette.responses import Response

from app.api.deps import get_current_user, require_role
from app.api.pagination import get_page_params
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.common import Page, PageParams
from app.schemas.subjects import (
    EnrollmentCreate,
    EnrollmentOut,
    SubjectCreate,
    SubjectOut,
    SubjectUpdate,
)
from app.services import subject_service

router = APIRouter(prefix="/subjects", tags=["subjects"])


@router.get("", response_model=Page[SubjectOut])
def list_subjects(
    mine: bool = Query(False),
    params: PageParams = Depends(get_page_params),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Page[SubjectOut]:
    return subject_service.list_subjects(db, current_user, mine=mine, params=params)


@router.post("", response_model=SubjectOut, status_code=201)
def create_subject(
    body: SubjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.TEACHER)),
) -> SubjectOut:
    return subject_service.create_subject(db, current_user, body)


@router.patch("/{subject_id}", response_model=SubjectOut)
def update_subject(
    subject_id: int,
    body: SubjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.TEACHER)),
) -> SubjectOut:
    return subject_service.update_subject(db, current_user, subject_id, body)


@router.post(
    "/{subject_id}/enrollments", response_model=EnrollmentOut, status_code=201
)
def enroll_student(
    subject_id: int,
    body: EnrollmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.TEACHER)),
) -> EnrollmentOut:
    return subject_service.enroll_student(db, current_user, subject_id, body)


@router.delete("/{subject_id}/enrollments/{student_id}", status_code=204)
def unenroll_student(
    subject_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.TEACHER)),
) -> Response:
    subject_service.unenroll_student(db, current_user, subject_id, student_id)
    return Response(status_code=204)
