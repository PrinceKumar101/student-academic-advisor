from collections.abc import Callable

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.errors import AppError, Forbidden, NotFound, Unauthenticated
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.enrollment import Enrollment
from app.models.enums import UserRole
from app.models.intervention import Intervention
from app.models.student import Student
from app.models.subject import Subject
from app.models.teaching_assignment import TeachingAssignment
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_current_user(
    db: Session = Depends(get_db),
    token: str | None = Depends(oauth2_scheme),
) -> User:
    if not token:
        raise Unauthenticated("Not authenticated")
    payload = decode_access_token(token)
    try:
        user_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError) as exc:
        raise Unauthenticated("Invalid or expired token") from exc
    user = db.execute(
        select(User)
        .options(selectinload(User.student), selectinload(User.teacher))
        .where(User.id == user_id)
    ).scalar_one_or_none()
    if user is None or not user.is_active:
        raise Unauthenticated("Invalid or expired token")
    return user


def require_role(*roles: UserRole) -> Callable[..., User]:
    def _require(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise Forbidden("Insufficient permissions")
        return current_user

    return _require


def visible_students_stmt(teacher_id: int):
    return (
        select(Student)
        .join(Enrollment, Enrollment.student_id == Student.id)
        .join(
            TeachingAssignment,
            TeachingAssignment.subject_id == Enrollment.subject_id,
        )
        .where(
            TeachingAssignment.teacher_id == teacher_id,
            or_(
                TeachingAssignment.section == "ALL",
                TeachingAssignment.section == Student.section,
            ),
        )
        .distinct()
    )


def list_visible_students(db: Session, teacher_id: int) -> list[Student]:
    return list(db.execute(visible_students_stmt(teacher_id)).scalars().unique().all())


def teacher_can_see_student(db: Session, teacher_id: int, student: Student) -> bool:
    stmt = (
        select(TeachingAssignment.id)
        .join(Enrollment, Enrollment.subject_id == TeachingAssignment.subject_id)
        .where(
            TeachingAssignment.teacher_id == teacher_id,
            Enrollment.student_id == student.id,
            or_(
                TeachingAssignment.section == "ALL",
                TeachingAssignment.section == student.section,
            ),
        )
        .limit(1)
    )
    return db.execute(stmt).first() is not None


def authorize_student_access(
    student_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Student:
    if student_id == "me":
        if current_user.role != UserRole.STUDENT or current_user.student is None:
            raise Forbidden("Only a student can use the 'me' student id")
        return current_user.student

    try:
        target_id = int(student_id)
    except ValueError as exc:
        raise AppError(
            "VALIDATION_ERROR",
            "student_id must be an integer or 'me'",
            422,
        ) from exc

    if current_user.role == UserRole.STUDENT:
        own = current_user.student
        if own is None or own.id != target_id:
            raise Forbidden("Cannot access another student's data")
        student = db.get(Student, target_id)
        if student is None:
            raise NotFound("Student not found")
        return student

    if current_user.role == UserRole.TEACHER:
        if current_user.teacher is None:
            raise Forbidden("Teacher profile is missing")
        student = db.get(Student, target_id)
        if student is None:
            raise NotFound("Student not found")
        if not teacher_can_see_student(db, current_user.teacher.id, student):
            raise Forbidden("Student is not visible to this teacher")
        return student

    raise Forbidden("Insufficient permissions")


def authorize_intervention_access(
    intervention_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Intervention:
    row = db.get(Intervention, intervention_id)
    if row is None:
        raise NotFound("Intervention not found")
    authorize_student_access(str(row.student_id), db=db, current_user=current_user)
    return row


def teacher_can_write_subject(
    db: Session,
    teacher_id: int,
    subject_id: int,
    student: Student | None = None,
) -> bool:
    stmt = select(TeachingAssignment).where(
        TeachingAssignment.teacher_id == teacher_id,
        TeachingAssignment.subject_id == subject_id,
    )
    assignments = db.execute(stmt).scalars().all()
    if not assignments:
        return False
    if student is None:
        return True
    return any(
        assignment.section == "ALL" or assignment.section == student.section
        for assignment in assignments
    )


def authorize_teacher_subject_write(
    db: Session,
    current_user: User,
    subject_id: int,
    student: Student | None = None,
) -> Subject:
    if current_user.role != UserRole.TEACHER or current_user.teacher is None:
        raise Forbidden("Only a teacher can modify academic records")
    subject = db.get(Subject, subject_id)
    if subject is None:
        raise NotFound("Subject not found")
    if not teacher_can_write_subject(
        db, current_user.teacher.id, subject_id, student
    ):
        raise Forbidden("Not assigned to this subject or section")
    return subject
