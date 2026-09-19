from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import authorize_student_access
from app.db.session import get_db
from app.models.student import Student
from app.schemas.trends import TrendsOut, WarningsOut
from app.services import trend_service

router = APIRouter(prefix="/trends", tags=["trends"])


@router.get("/{student_id}/warnings", response_model=WarningsOut)
def get_warnings(
    student: Student = Depends(authorize_student_access),
    db: Session = Depends(get_db),
    as_of: date | None = Query(default=None),
) -> WarningsOut:
    return trend_service.get_warnings(db, student, as_of or date.today())


@router.get("/{student_id}", response_model=TrendsOut)
def get_trends(
    student: Student = Depends(authorize_student_access),
    db: Session = Depends(get_db),
    as_of: date | None = Query(default=None),
) -> TrendsOut:
    return trend_service.get_trends(db, student, as_of or date.today())
