from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import authorize_student_access
from app.db.session import get_db
from app.models.student import Student
from app.schemas.risk import RiskHistoryOut, RiskOut, WhatIfOut, WhatIfRequest
from app.services import risk_service, whatif_service

router = APIRouter(prefix="/risk", tags=["risk"])


@router.post("/{student_id}/what-if", response_model=WhatIfOut)
def post_what_if(
    body: WhatIfRequest,
    student: Student = Depends(authorize_student_access),
    db: Session = Depends(get_db),
    as_of: date | None = Query(default=None),
) -> WhatIfOut:
    return whatif_service.run_what_if(
        db, student, body.overrides.applied(), as_of or date.today()
    )


@router.get("/{student_id}/history", response_model=RiskHistoryOut)
def get_risk_history(
    student: Student = Depends(authorize_student_access),
    db: Session = Depends(get_db),
) -> RiskHistoryOut:
    return risk_service.get_history(db, student)


@router.get("/{student_id}", response_model=RiskOut)
def get_risk(
    student: Student = Depends(authorize_student_access),
    db: Session = Depends(get_db),
    as_of: date | None = Query(default=None),
) -> RiskOut:
    return risk_service.get_current(db, student, as_of or date.today())
