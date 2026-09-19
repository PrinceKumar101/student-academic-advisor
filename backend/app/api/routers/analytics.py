from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import authorize_student_access
from app.db.session import get_db
from app.models.student import Student
from app.schemas.analytics import ComparisonOut, SubjectAnalysisListOut
from app.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get(
    "/students/{student_id}/subjects",
    response_model=SubjectAnalysisListOut,
)
def get_student_subjects(
    student: Student = Depends(authorize_student_access),
    db: Session = Depends(get_db),
    as_of: date | None = Query(default=None),
) -> SubjectAnalysisListOut:
    return analytics_service.get_subject_analysis(db, student, as_of or date.today())


@router.get(
    "/students/{student_id}/comparison",
    response_model=ComparisonOut,
)
def get_student_comparison(
    student: Student = Depends(authorize_student_access),
    db: Session = Depends(get_db),
    as_of: date | None = Query(default=None),
) -> ComparisonOut:
    return analytics_service.get_comparison(db, student, as_of or date.today())
