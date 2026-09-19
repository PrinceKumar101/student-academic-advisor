from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.api.pagination import get_page_params
from app.db.session import get_db
from app.models.enums import RiskLevel, UserRole
from app.models.user import User
from app.schemas.common import Page, PageParams
from app.schemas.teacher import (
    SubjectAnalyticsOut,
    TeacherDashboardOut,
    TeacherStudentOut,
)
from app.services import teacher_service

router = APIRouter(prefix="/teacher", tags=["teacher"])


@router.get("/dashboard", response_model=TeacherDashboardOut)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.TEACHER)),
    as_of: date | None = Query(default=None),
) -> TeacherDashboardOut:
    return teacher_service.get_dashboard(db, current_user, as_of=as_of)


@router.get("/students", response_model=Page[TeacherStudentOut])
def list_students(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.TEACHER)),
    params: PageParams = Depends(get_page_params),
    risk_level: RiskLevel | None = Query(default=None),
    department: str | None = Query(default=None),
    semester: int | None = Query(default=None),
    section: str | None = Query(default=None),
    subject_id: int | None = Query(default=None),
    search: str | None = Query(default=None),
    as_of: date | None = Query(default=None),
) -> Page[TeacherStudentOut]:
    return teacher_service.list_students(
        db,
        current_user,
        params,
        risk_level=risk_level,
        department=department,
        semester=semester,
        section=section,
        subject_id=subject_id,
        search=search,
        as_of=as_of,
    )


@router.get(
    "/subjects/{subject_id}/analytics",
    response_model=SubjectAnalyticsOut,
)
def get_subject_analytics(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.TEACHER)),
    as_of: date | None = Query(default=None),
) -> SubjectAnalyticsOut:
    return teacher_service.get_subject_analytics(
        db, current_user, subject_id, as_of=as_of
    )
