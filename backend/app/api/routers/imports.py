from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.imports import ImportResultOut
from app.services import import_service

router = APIRouter(prefix="/imports", tags=["imports"])


@router.post("/attendance", response_model=ImportResultOut)
async def import_attendance(
    file: UploadFile = File(...),
    dry_run: bool = Query(default=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.TEACHER)),
) -> ImportResultOut:
    content = await file.read()
    return import_service.import_attendance(db, current_user, content, dry_run=dry_run)


@router.post("/assessments", response_model=ImportResultOut)
async def import_assessments(
    file: UploadFile = File(...),
    dry_run: bool = Query(default=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.TEACHER)),
) -> ImportResultOut:
    content = await file.read()
    return import_service.import_assessments(db, current_user, content, dry_run=dry_run)
