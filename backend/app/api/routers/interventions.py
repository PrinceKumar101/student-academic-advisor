from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import authorize_intervention_access, get_current_user, require_role
from app.db.session import get_db
from app.models.enums import InterventionStatus, UserRole
from app.models.intervention import Intervention
from app.models.user import User
from app.schemas.interventions import (
    InterventionCreate,
    InterventionOut,
    InterventionPatch,
    InterventionProgressOut,
)
from app.services import intervention_service

router = APIRouter(prefix="/interventions", tags=["interventions"])


@router.post("", response_model=InterventionOut, status_code=201)
def create_intervention(
    body: InterventionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.TEACHER)),
    as_of: date | None = Query(default=None),
) -> InterventionOut:
    return intervention_service.create_intervention(
        db, current_user, body, as_of=as_of
    )


@router.get("", response_model=list[InterventionOut])
def list_interventions(
    student_id: int | None = Query(default=None),
    status: InterventionStatus | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[InterventionOut]:
    return intervention_service.list_interventions(
        db, current_user, student_id=student_id, status=status
    )


@router.get("/{intervention_id}", response_model=InterventionOut)
def get_intervention(
    intervention: Intervention = Depends(authorize_intervention_access),
) -> InterventionOut:
    return intervention_service.get_intervention(intervention)


@router.patch("/{intervention_id}", response_model=InterventionOut)
def patch_intervention(
    body: InterventionPatch,
    intervention: Intervention = Depends(authorize_intervention_access),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    as_of: date | None = Query(default=None),
) -> InterventionOut:
    return intervention_service.patch_intervention(
        db, current_user, intervention, body, as_of=as_of
    )


@router.get(
    "/{intervention_id}/progress",
    response_model=InterventionProgressOut,
)
def get_progress(
    intervention: Intervention = Depends(authorize_intervention_access),
    db: Session = Depends(get_db),
    as_of: date | None = Query(default=None),
) -> InterventionProgressOut:
    return intervention_service.get_progress(db, intervention, as_of=as_of)
