from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from starlette.responses import Response

from app.api.deps import authorize_student_access, get_current_user, require_role
from app.db.session import get_db
from app.models.enums import AssessmentType, UserRole
from app.models.user import User
from app.schemas.assessments import AssessmentCreate, AssessmentOut, AssessmentUpdate
from app.services import assessment_service

router = APIRouter(prefix="/assessments", tags=["assessments"])


@router.get("", response_model=list[AssessmentOut])
def list_assessments(
    student_id: str = Query("me"),
    subject_id: int | None = None,
    type: AssessmentType | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[AssessmentOut]:
    student = authorize_student_access(student_id, db, current_user)
    return assessment_service.list_assessments(
        db, student, subject_id=subject_id, assessment_type=type
    )


@router.post("", response_model=AssessmentOut, status_code=201)
def create_assessment(
    body: AssessmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.TEACHER)),
) -> AssessmentOut:
    return assessment_service.create_assessment(db, current_user, body)


@router.put("/{assessment_id}", response_model=AssessmentOut)
def update_assessment(
    assessment_id: int,
    body: AssessmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.TEACHER)),
) -> AssessmentOut:
    return assessment_service.update_assessment(
        db, current_user, assessment_id, body
    )


@router.delete("/{assessment_id}", status_code=204)
def delete_assessment(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.TEACHER)),
) -> Response:
    assessment_service.delete_assessment(db, current_user, assessment_id)
    return Response(status_code=204)
