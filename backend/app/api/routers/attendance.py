from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from starlette.responses import Response

from app.api.deps import authorize_student_access, get_current_user, require_role
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.attendance import (
    AttendanceListOut,
    AttendanceRecordCreate,
    AttendanceRecordOut,
    AttendanceRecordUpdate,
)
from app.services import attendance_service

router = APIRouter(prefix="/attendance", tags=["attendance"])


@router.get("", response_model=AttendanceListOut)
def list_attendance(
    student_id: str = Query("me"),
    subject_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AttendanceListOut:
    student = authorize_student_access(student_id, db, current_user)
    return attendance_service.list_attendance(db, student, subject_id)


@router.post("", response_model=AttendanceRecordOut, status_code=201)
def create_attendance(
    body: AttendanceRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.TEACHER)),
) -> AttendanceRecordOut:
    return attendance_service.create_attendance(db, current_user, body)


@router.put("/{record_id}", response_model=AttendanceRecordOut)
def update_attendance(
    record_id: int,
    body: AttendanceRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.TEACHER)),
) -> AttendanceRecordOut:
    return attendance_service.update_attendance(db, current_user, record_id, body)


@router.delete("/{record_id}", status_code=204)
def delete_attendance(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.TEACHER)),
) -> Response:
    attendance_service.delete_attendance(db, current_user, record_id)
    return Response(status_code=204)
