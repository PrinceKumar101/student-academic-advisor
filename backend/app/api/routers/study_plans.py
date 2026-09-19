from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.ai.client import AIClient, get_ai_client
from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.study_plans import (
    StudyPlanCreate,
    StudyPlanItemOut,
    StudyPlanItemPatch,
    StudyPlanOut,
    StudyPlanSummaryOut,
)
from app.services import study_plan_service

router = APIRouter(prefix="/study-plans", tags=["study-plans"])


@router.post("", response_model=StudyPlanOut)
def create_study_plan(
    body: StudyPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    client: AIClient = Depends(get_ai_client),
) -> StudyPlanOut:
    return study_plan_service.create_plan(db, current_user, body, client=client)


@router.get("", response_model=list[StudyPlanSummaryOut])
def list_study_plans(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT)),
) -> list[StudyPlanSummaryOut]:
    return study_plan_service.list_plans(db, current_user)


@router.get("/{plan_id}", response_model=StudyPlanOut)
def get_study_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StudyPlanOut:
    return study_plan_service.get_plan(db, current_user, plan_id)


@router.patch("/{plan_id}/items/{item_id}", response_model=StudyPlanItemOut)
def patch_study_plan_item(
    plan_id: int,
    item_id: int,
    body: StudyPlanItemPatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StudyPlanItemOut:
    return study_plan_service.patch_item(
        db, current_user, plan_id, item_id, is_completed=body.is_completed
    )


@router.delete("/{plan_id}", status_code=204)
def delete_study_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    study_plan_service.delete_plan(db, current_user, plan_id)
    return Response(status_code=204)
