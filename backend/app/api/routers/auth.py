from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette.responses import Response

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    MeResponse,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)
from app.services.auth_service import current_user_payload, login, register_student

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse, status_code=201)
def register(body: RegisterRequest, db: Session = Depends(get_db)) -> RegisterResponse:
    return register_student(db, body)


@router.post("/login", response_model=TokenResponse)
def login_for_token(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> TokenResponse:
    return login(db, form.username, form.password)


@router.post("/logout", status_code=204)
def logout(_current_user: User = Depends(get_current_user)) -> Response:
    return Response(status_code=204)


@router.get("/me", response_model=MeResponse)
def me(current_user: User = Depends(get_current_user)) -> MeResponse:
    return current_user_payload(current_user)
