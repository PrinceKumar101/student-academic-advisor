from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.core.errors import Conflict, Unauthenticated
from app.core.security import create_access_token, hash_password, verify_password
from app.models.enums import UserRole
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.user import User
from app.schemas.auth import (
    LOGIN_FAILURE_MESSAGE,
    AuthUserOut,
    MeResponse,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)


def _profile_ids(user: User) -> tuple[int | None, int | None, str]:
    if user.student is not None:
        return user.student.id, None, user.student.full_name
    if user.teacher is not None:
        return None, user.teacher.id, user.teacher.full_name
    return None, None, ""


def _auth_user_out(user: User) -> AuthUserOut:
    student_id, teacher_id, full_name = _profile_ids(user)
    return AuthUserOut(
        id=user.id,
        role=user.role,
        student_id=student_id,
        teacher_id=teacher_id,
        full_name=full_name,
    )


def register_student(db: Session, body: RegisterRequest) -> RegisterResponse:
    email = body.email.strip().lower()
    existing_email = db.execute(
        select(User).where(User.email == email)
    ).scalar_one_or_none()
    if existing_email is not None:
        raise Conflict("Email already registered")
    existing_code = db.execute(
        select(Student).where(Student.student_code == body.student_code)
    ).scalar_one_or_none()
    if existing_code is not None:
        raise Conflict("Student code already registered")

    user = User(
        email=email,
        password_hash=hash_password(body.password),
        role=UserRole.STUDENT,
    )
    db.add(user)
    try:
        db.flush()
        student = Student(
            user_id=user.id,
            student_code=body.student_code,
            full_name=body.full_name,
            department=body.department,
            semester=body.semester,
            section=body.section,
        )
        db.add(student)
        db.commit()
        db.refresh(user)
        db.refresh(student)
    except IntegrityError as exc:
        db.rollback()
        raise Conflict("Email or student code already registered") from exc
    return RegisterResponse(user_id=user.id, student_id=student.id)


def login(db: Session, email: str, password: str) -> TokenResponse:
    normalized = email.strip().lower()
    user = db.execute(
        select(User)
        .options(selectinload(User.student), selectinload(User.teacher))
        .where(User.email == normalized)
    ).scalar_one_or_none()
    if (
        user is None
        or not user.is_active
        or not verify_password(password, user.password_hash)
    ):
        raise Unauthenticated(LOGIN_FAILURE_MESSAGE)

    settings = get_settings()
    token = create_access_token(user_id=user.id, role=user.role.value)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.jwt_expire_minutes * 60,
        user=_auth_user_out(user),
    )


def current_user_payload(user: User) -> MeResponse:
    student_id, teacher_id, full_name = _profile_ids(user)
    return MeResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        student_id=student_id,
        teacher_id=teacher_id,
        full_name=full_name,
    )


def create_teacher_account(
    db: Session,
    *,
    email: str,
    password: str,
    full_name: str,
    department: str,
) -> Teacher:
    normalized = email.strip().lower()
    existing = db.execute(
        select(User).where(User.email == normalized)
    ).scalar_one_or_none()
    if existing is not None:
        raise Conflict("Email already registered")
    user = User(
        email=normalized,
        password_hash=hash_password(password),
        role=UserRole.TEACHER,
    )
    db.add(user)
    try:
        db.flush()
        teacher = Teacher(
            user_id=user.id,
            full_name=full_name,
            department=department,
        )
        db.add(teacher)
        db.commit()
        db.refresh(teacher)
    except IntegrityError as exc:
        db.rollback()
        raise Conflict("Email already registered") from exc
    return teacher
