from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.ai.client import AIClient, get_ai_client
from app.api.deps import authorize_student_access, get_current_user, require_role
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.ai import (
    AnalysisOut,
    AnalysisRequest,
    ChatHistoryOut,
    ChatOut,
    ChatRequest,
    InterventionSuggestionsOut,
    InterventionSuggestionsRequest,
    UsageOut,
)
from app.services import ai_service

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/usage", response_model=UsageOut)
def get_usage(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UsageOut:
    return ai_service.usage_for_user(db, current_user)


@router.post(
    "/intervention-suggestions",
    response_model=InterventionSuggestionsOut,
)
def post_intervention_suggestions(
    body: InterventionSuggestionsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.TEACHER)),
    client: AIClient = Depends(get_ai_client),
) -> InterventionSuggestionsOut:
    student = authorize_student_access(
        body.student_id, db=db, current_user=current_user
    )
    return ai_service.suggest_interventions(db, student, current_user, client=client)


@router.post("/analysis", response_model=AnalysisOut)
def post_analysis(
    body: AnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    client: AIClient = Depends(get_ai_client),
) -> AnalysisOut:
    student = authorize_student_access(
        body.student_id, db=db, current_user=current_user
    )
    return ai_service.analyze_performance(
        db,
        student,
        current_user,
        refresh=body.refresh,
        client=client,
    )


@router.get("/chat/history", response_model=ChatHistoryOut)
def get_chat_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT)),
) -> ChatHistoryOut:
    return ai_service.list_chat_history(db, current_user)


@router.delete("/chat/history", status_code=204)
def delete_chat_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT)),
) -> Response:
    ai_service.clear_chat_history(db, current_user)
    return Response(status_code=204)


@router.post("/chat", response_model=ChatOut)
def post_chat(
    body: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    client: AIClient = Depends(get_ai_client),
) -> ChatOut:
    return ai_service.answer_academic_question(
        db,
        current_user,
        body.question,
        client=client,
    )
