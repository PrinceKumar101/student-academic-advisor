from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import authorize_teacher_subject_write
from app.api.pagination import page_offset, to_page
from app.core.errors import Conflict, NotFound
from app.models.enrollment import Enrollment
from app.models.enums import UserRole
from app.models.student import Student
from app.models.subject import Subject
from app.models.teaching_assignment import TeachingAssignment
from app.models.user import User
from app.schemas.common import Page, PageParams
from app.schemas.subjects import (
    EnrollmentCreate,
    EnrollmentOut,
    SubjectCreate,
    SubjectOut,
    SubjectUpdate,
)


def _subject_out(subject: Subject) -> SubjectOut:
    return SubjectOut.model_validate(subject)


def list_subjects(
    db: Session,
    current_user: User,
    *,
    mine: bool,
    params: PageParams,
) -> Page[SubjectOut]:
    stmt = select(Subject)
    count_stmt = select(func.count()).select_from(Subject)
    if mine:
        if current_user.role == UserRole.STUDENT:
            if current_user.student is None:
                return Page(
                    items=[], total=0, page=params.page, page_size=params.page_size
                )
            stmt = stmt.join(Enrollment).where(
                Enrollment.student_id == current_user.student.id
            )
            count_stmt = (
                select(func.count())
                .select_from(Subject)
                .join(Enrollment)
                .where(Enrollment.student_id == current_user.student.id)
            )
        elif current_user.role == UserRole.TEACHER:
            if current_user.teacher is None:
                return Page(
                    items=[], total=0, page=params.page, page_size=params.page_size
                )
            stmt = (
                stmt.join(TeachingAssignment)
                .where(TeachingAssignment.teacher_id == current_user.teacher.id)
                .distinct()
            )
            count_stmt = (
                select(func.count(func.distinct(Subject.id)))
                .select_from(Subject)
                .join(TeachingAssignment)
                .where(TeachingAssignment.teacher_id == current_user.teacher.id)
            )
    total = db.execute(count_stmt).scalar_one()
    rows = db.execute(
        stmt.order_by(Subject.code)
        .offset(page_offset(params))
        .limit(params.page_size)
    ).scalars().all()
    return to_page([_subject_out(row) for row in rows], total, params)


def create_subject(
    db: Session, current_user: User, body: SubjectCreate
) -> SubjectOut:
    if current_user.teacher is None:
        raise NotFound("Teacher profile is missing")
    existing = db.execute(
        select(Subject).where(Subject.code == body.code.strip())
    ).scalar_one_or_none()
    if existing is not None:
        raise Conflict("Subject code already exists")
    subject = Subject(
        code=body.code.strip(),
        name=body.name.strip(),
        semester=body.semester,
    )
    db.add(subject)
    try:
        db.flush()
        db.add(
            TeachingAssignment(
                teacher_id=current_user.teacher.id,
                subject_id=subject.id,
                section="ALL",
            )
        )
        db.commit()
        db.refresh(subject)
    except IntegrityError as exc:
        db.rollback()
        raise Conflict("Subject code already exists") from exc
    return _subject_out(subject)


def update_subject(
    db: Session, current_user: User, subject_id: int, body: SubjectUpdate
) -> SubjectOut:
    subject = authorize_teacher_subject_write(db, current_user, subject_id)
    data = body.model_dump(exclude_unset=True)
    if "code" in data and data["code"] is not None:
        data["code"] = data["code"].strip()
        clash = db.execute(
            select(Subject).where(
                Subject.code == data["code"], Subject.id != subject_id
            )
        ).scalar_one_or_none()
        if clash is not None:
            raise Conflict("Subject code already exists")
    if "name" in data and data["name"] is not None:
        data["name"] = data["name"].strip()
    for key, value in data.items():
        setattr(subject, key, value)
    try:
        db.commit()
        db.refresh(subject)
    except IntegrityError as exc:
        db.rollback()
        raise Conflict("Subject code already exists") from exc
    return _subject_out(subject)


def enroll_student(
    db: Session, current_user: User, subject_id: int, body: EnrollmentCreate
) -> EnrollmentOut:
    student = db.get(Student, body.student_id)
    if student is None:
        raise NotFound("Student not found")
    authorize_teacher_subject_write(db, current_user, subject_id, student)
    existing = db.execute(
        select(Enrollment).where(
            Enrollment.student_id == student.id,
            Enrollment.subject_id == subject_id,
        )
    ).scalar_one_or_none()
    if existing is not None:
        raise Conflict("Student is already enrolled in this subject")
    enrollment = Enrollment(student_id=student.id, subject_id=subject_id)
    db.add(enrollment)
    try:
        db.commit()
        db.refresh(enrollment)
    except IntegrityError as exc:
        db.rollback()
        raise Conflict("Student is already enrolled in this subject") from exc
    return EnrollmentOut.model_validate(enrollment)


def unenroll_student(
    db: Session, current_user: User, subject_id: int, student_id: int
) -> None:
    student = db.get(Student, student_id)
    if student is None:
        raise NotFound("Student not found")
    authorize_teacher_subject_write(db, current_user, subject_id, student)
    enrollment = db.execute(
        select(Enrollment).where(
            Enrollment.student_id == student_id,
            Enrollment.subject_id == subject_id,
        )
    ).scalar_one_or_none()
    if enrollment is None:
        raise NotFound("Enrollment not found")
    db.delete(enrollment)
    db.commit()
