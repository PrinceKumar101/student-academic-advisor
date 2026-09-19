from datetime import UTC, date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import (
    authorize_student_access,
    teacher_can_write_subject,
)
from app.core.errors import AppError, Forbidden, NotFound
from app.engines.intervention_progress import (
    PROGRESS_NOTE,
    progress_change,
    progress_direction,
)
from app.engines.risk_config import round1
from app.models.enrollment import Enrollment
from app.models.enums import InterventionStatus, UserRole
from app.models.intervention import Intervention
from app.models.student import Student
from app.models.user import User
from app.schemas.interventions import (
    InterventionCreate,
    InterventionOut,
    InterventionPatch,
    InterventionProgressOut,
    RiskSnapshotOut,
)
from app.services.risk_service import compute_for_student

_STUDENT_FORWARD: dict[InterventionStatus, set[InterventionStatus]] = {
    InterventionStatus.PENDING: {InterventionStatus.IN_PROGRESS},
    InterventionStatus.IN_PROGRESS: {InterventionStatus.COMPLETED},
    InterventionStatus.COMPLETED: set(),
}

_TEACHER_ONLY_FIELDS = (
    "title",
    "description",
    "priority",
    "due_date",
    "subject_id",
)


def _to_out(row: Intervention) -> InterventionOut:
    return InterventionOut(
        id=row.id,
        student_id=row.student_id,
        teacher_id=row.teacher_id,
        subject_id=row.subject_id,
        title=row.title,
        description=row.description,
        priority=row.priority,
        status=row.status,
        due_date=row.due_date,
        baseline_score=row.baseline_score,
        baseline_level=row.baseline_level,
        baseline_at=row.baseline_at,
        outcome_score=row.outcome_score,
        outcome_level=row.outcome_level,
        outcome_at=row.outcome_at,
        completion_note=row.completion_note,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _require_teacher(user: User) -> int:
    if user.role != UserRole.TEACHER or user.teacher is None:
        raise Forbidden("Only a teacher can create interventions")
    return user.teacher.id


def _validate_optional_subject(
    db: Session, teacher_id: int, student: Student, subject_id: int | None
) -> None:
    if subject_id is None:
        return
    enrolled = db.execute(
        select(Enrollment.id).where(
            Enrollment.student_id == student.id,
            Enrollment.subject_id == subject_id,
        )
    ).first()
    if enrolled is None:
        raise AppError(
            "VALIDATION_ERROR",
            "Student is not enrolled in that subject",
            422,
        )
    if not teacher_can_write_subject(db, teacher_id, subject_id, student):
        raise Forbidden("Not assigned to this subject or section")


def create_intervention(
    db: Session,
    user: User,
    body: InterventionCreate,
    *,
    as_of: date | None = None,
    now: datetime | None = None,
) -> InterventionOut:
    teacher_id = _require_teacher(user)
    as_of = as_of or date.today()
    now = now or datetime.now(UTC)
    student = authorize_student_access(
        str(body.student_id), db=db, current_user=user
    )
    _validate_optional_subject(db, teacher_id, student, body.subject_id)
    risk = compute_for_student(db, student, as_of)
    row = Intervention(
        student_id=student.id,
        teacher_id=teacher_id,
        subject_id=body.subject_id,
        title=body.title.strip(),
        description=body.description,
        priority=body.priority,
        status=InterventionStatus.PENDING,
        due_date=body.due_date,
        baseline_score=risk.score,
        baseline_level=risk.level,
        baseline_at=now,
        created_at=now,
        updated_at=now,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _to_out(row)


_OPEN_STATUSES = (
    InterventionStatus.PENDING,
    InterventionStatus.IN_PROGRESS,
)


def list_open_for_student(db: Session, student_id: int) -> list[InterventionOut]:
    rows = db.execute(
        select(Intervention)
        .where(
            Intervention.student_id == student_id,
            Intervention.status.in_(_OPEN_STATUSES),
        )
        .order_by(Intervention.created_at.desc(), Intervention.id.desc())
    ).scalars().all()
    return [_to_out(row) for row in rows]


def list_interventions(
    db: Session,
    user: User,
    *,
    student_id: int | None = None,
    status: InterventionStatus | None = None,
) -> list[InterventionOut]:
    stmt = select(Intervention)
    if user.role == UserRole.STUDENT:
        if user.student is None:
            raise Forbidden("Student profile is missing")
        if student_id is not None and student_id != user.student.id:
            raise Forbidden("Cannot access another student's data")
        stmt = stmt.where(Intervention.student_id == user.student.id)
    elif user.role == UserRole.TEACHER:
        if user.teacher is None:
            raise Forbidden("Teacher profile is missing")
        if student_id is not None:
            authorize_student_access(str(student_id), db=db, current_user=user)
            stmt = stmt.where(Intervention.student_id == student_id)
        else:
            from app.api.deps import list_visible_students

            visible_ids = [
                item.id for item in list_visible_students(db, user.teacher.id)
            ]
            stmt = stmt.where(Intervention.student_id.in_(visible_ids or [-1]))
    else:
        raise Forbidden("Insufficient permissions")

    if status is not None:
        stmt = stmt.where(Intervention.status == status)
    stmt = stmt.order_by(Intervention.created_at.desc(), Intervention.id.desc())
    return [_to_out(row) for row in db.execute(stmt).scalars().all()]


def get_intervention(row: Intervention) -> InterventionOut:
    return _to_out(row)


def _apply_teacher_fields(
    db: Session,
    user: User,
    row: Intervention,
    body: InterventionPatch,
    student: Student,
) -> None:
    data = body.model_dump(exclude_unset=True)
    if "subject_id" in data:
        _validate_optional_subject(db, user.teacher.id, student, data["subject_id"])
        row.subject_id = data["subject_id"]
    if "title" in data and data["title"] is not None:
        row.title = data["title"].strip()
    if "description" in data:
        row.description = data["description"]
    if "priority" in data and data["priority"] is not None:
        row.priority = data["priority"]
    if "due_date" in data:
        row.due_date = data["due_date"]


def _capture_outcome(
    db: Session,
    row: Intervention,
    student: Student,
    *,
    as_of: date,
    now: datetime,
) -> None:
    risk = compute_for_student(db, student, as_of)
    row.outcome_score = risk.score
    row.outcome_level = risk.level
    row.outcome_at = now


def patch_intervention(
    db: Session,
    user: User,
    row: Intervention,
    body: InterventionPatch,
    *,
    as_of: date | None = None,
    now: datetime | None = None,
) -> InterventionOut:
    as_of = as_of or date.today()
    now = now or datetime.now(UTC)
    student = db.get(Student, row.student_id)
    if student is None:
        raise NotFound("Student not found")

    data = body.model_dump(exclude_unset=True)
    if user.role == UserRole.STUDENT:
        extra = [name for name in _TEACHER_ONLY_FIELDS if name in data]
        if extra:
            raise Forbidden("Students may only update status and completion_note")
        if "status" in data and data["status"] is not None:
            target = data["status"]
            if target not in _STUDENT_FORWARD[row.status]:
                raise AppError(
                    "VALIDATION_ERROR",
                    "Students may only move status forward "
                    "(PENDING → IN_PROGRESS → COMPLETED)",
                    422,
                )
            if (
                target is InterventionStatus.COMPLETED
                and row.status is not InterventionStatus.COMPLETED
            ):
                _capture_outcome(db, row, student, as_of=as_of, now=now)
            row.status = target
        if "completion_note" in data:
            row.completion_note = data["completion_note"]
    elif user.role == UserRole.TEACHER:
        _apply_teacher_fields(db, user, row, body, student)
        if "completion_note" in data:
            row.completion_note = data["completion_note"]
        if "status" in data and data["status"] is not None:
            target = data["status"]
            if (
                target is InterventionStatus.COMPLETED
                and row.status is not InterventionStatus.COMPLETED
            ):
                _capture_outcome(db, row, student, as_of=as_of, now=now)
            row.status = target
    else:
        raise Forbidden("Insufficient permissions")

    row.updated_at = now
    db.commit()
    db.refresh(row)
    return _to_out(row)


def get_progress(
    db: Session,
    row: Intervention,
    *,
    as_of: date | None = None,
) -> InterventionProgressOut:
    as_of = as_of or date.today()
    student = db.get(Student, row.student_id)
    if student is None:
        raise NotFound("Student not found")
    current = compute_for_student(db, student, as_of)
    change = progress_change(current.score, row.baseline_score)
    if change is not None:
        change = round1(change)
    baseline_date = row.baseline_at.date() if row.baseline_at else as_of
    return InterventionProgressOut(
        baseline=RiskSnapshotOut(
            score=row.baseline_score,
            level=row.baseline_level,
            at=row.baseline_at,
        ),
        current=RiskSnapshotOut(
            score=current.score,
            level=current.level,
            as_of=as_of,
        ),
        change=change,
        direction=progress_direction(change),
        days_elapsed=max(0, (as_of - baseline_date).days),
        note=PROGRESS_NOTE,
    )
