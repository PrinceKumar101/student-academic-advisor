from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import authorize_teacher_subject_write
from app.core.errors import AppError, NotFound
from app.models.assessment import Assessment
from app.models.enrollment import Enrollment
from app.models.enums import AssessmentStatus, AssessmentType
from app.models.student import Student
from app.models.user import User
from app.schemas.assessments import AssessmentCreate, AssessmentOut, AssessmentUpdate


def _assessment_out(row: Assessment) -> AssessmentOut:
    return AssessmentOut(
        id=row.id,
        student_id=row.enrollment.student_id,
        subject_id=row.enrollment.subject_id,
        type=row.type,
        name=row.name,
        max_marks=row.max_marks,
        obtained_marks=row.obtained_marks,
        status=row.status,
        assessment_date=row.assessment_date,
    )


def _get_enrollment(db: Session, student_id: int, subject_id: int) -> Enrollment:
    enrollment = db.execute(
        select(Enrollment).where(
            Enrollment.student_id == student_id,
            Enrollment.subject_id == subject_id,
        )
    ).scalar_one_or_none()
    if enrollment is None:
        raise NotFound("Enrollment not found")
    return enrollment


def list_assessments(
    db: Session,
    student: Student,
    *,
    subject_id: int | None,
    assessment_type: AssessmentType | None,
) -> list[AssessmentOut]:
    stmt = (
        select(Assessment)
        .join(Enrollment)
        .options(selectinload(Assessment.enrollment))
        .where(Enrollment.student_id == student.id)
        .order_by(Assessment.assessment_date, Assessment.id)
    )
    if subject_id is not None:
        stmt = stmt.where(Enrollment.subject_id == subject_id)
    if assessment_type is not None:
        stmt = stmt.where(Assessment.type == assessment_type)
    rows = db.execute(stmt).scalars().all()
    return [_assessment_out(row) for row in rows]


def create_assessment(
    db: Session, current_user: User, body: AssessmentCreate
) -> AssessmentOut:
    student = db.get(Student, body.student_id)
    if student is None:
        raise NotFound("Student not found")
    authorize_teacher_subject_write(db, current_user, body.subject_id, student)
    enrollment = _get_enrollment(db, body.student_id, body.subject_id)
    row = Assessment(
        enrollment_id=enrollment.id,
        type=body.type,
        name=body.name.strip(),
        max_marks=body.max_marks,
        obtained_marks=body.obtained_marks,
        status=body.status,
        assessment_date=body.assessment_date,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    row = db.execute(
        select(Assessment)
        .options(selectinload(Assessment.enrollment))
        .where(Assessment.id == row.id)
    ).scalar_one()
    return _assessment_out(row)


def _loaded(db: Session, assessment_id: int) -> Assessment:
    row = db.execute(
        select(Assessment)
        .options(
            selectinload(Assessment.enrollment).selectinload(Enrollment.student)
        )
        .where(Assessment.id == assessment_id)
    ).scalar_one_or_none()
    if row is None:
        raise NotFound("Assessment not found")
    return row


def _validate_marks(
    status: AssessmentStatus,
    max_marks: float,
    obtained_marks: float | None,
) -> None:
    if obtained_marks is not None and obtained_marks > max_marks:
        raise AppError(
            "VALIDATION_ERROR",
            "obtained_marks cannot exceed max_marks",
            422,
        )
    if status == AssessmentStatus.GRADED and obtained_marks is None:
        raise AppError(
            "VALIDATION_ERROR",
            "GRADED assessments require obtained_marks",
            422,
        )


def update_assessment(
    db: Session, current_user: User, assessment_id: int, body: AssessmentUpdate
) -> AssessmentOut:
    row = _loaded(db, assessment_id)
    authorize_teacher_subject_write(
        db, current_user, row.enrollment.subject_id, row.enrollment.student
    )
    data = body.model_dump(exclude_unset=True)
    if "name" in data and data["name"] is not None:
        data["name"] = data["name"].strip()
    status = data.get("status", row.status)
    max_marks = data.get("max_marks", row.max_marks)
    obtained = data.get("obtained_marks", row.obtained_marks)
    _validate_marks(status, max_marks, obtained)
    for key, value in data.items():
        setattr(row, key, value)
    db.commit()
    db.refresh(row)
    return _assessment_out(row)


def delete_assessment(db: Session, current_user: User, assessment_id: int) -> None:
    row = _loaded(db, assessment_id)
    authorize_teacher_subject_write(
        db, current_user, row.enrollment.subject_id, row.enrollment.student
    )
    db.delete(row)
    db.commit()
