from datetime import UTC, date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.engines.metrics import to_risk_inputs
from app.engines.risk_config import RiskValidationError
from app.engines.risk_engine import RiskResult, compute_risk
from app.models.risk_assessment import RiskAssessment
from app.models.student import Student
from app.schemas.risk import (
    RiskComponentOut,
    RiskHistoryItemOut,
    RiskHistoryOut,
    RiskOut,
)
from app.services.academic_data_loader import load


def _scores_equal(left: float | None, right: float | None) -> bool:
    if left is None or right is None:
        return left is None and right is None
    return round(left, 1) == round(right, 1)


def _to_out(student_id: int, as_of: date, result: RiskResult) -> RiskOut:
    return RiskOut(
        student_id=student_id,
        as_of=as_of,
        score=result.score,
        level=result.level,
        escalated=result.escalated,
        escalation_reason=result.escalation_reason,
        data_completeness=result.data_completeness,
        config_version=result.config_version,
        components=[
            RiskComponentOut.model_validate(item)
            for item in result.components_payload()
        ],
        top_factors=list(result.top_factors),
        flags=list(result.flags),
    )


def _persist_if_needed(
    db: Session,
    student_id: int,
    as_of: date,
    result: RiskResult,
    *,
    computed_at: datetime | None = None,
) -> None:
    latest = db.execute(
        select(RiskAssessment)
        .where(RiskAssessment.student_id == student_id)
        .order_by(RiskAssessment.computed_at.desc(), RiskAssessment.id.desc())
        .limit(1)
    ).scalar_one_or_none()
    if (
        latest is not None
        and latest.as_of == as_of
        and _scores_equal(latest.score, result.score)
        and latest.level == result.level
    ):
        return

    db.add(
        RiskAssessment(
            student_id=student_id,
            computed_at=computed_at or datetime.now(UTC),
            as_of=as_of,
            score=result.score,
            level=result.level,
            escalated=result.escalated,
            escalation_reason=result.escalation_reason,
            data_completeness=result.data_completeness,
            config_version=result.config_version,
            components=result.components_payload(),
            flags=list(result.flags),
        )
    )
    db.commit()


def compute_for_student(
    db: Session,
    student: Student,
    as_of: date,
    *,
    persist: bool = True,
    computed_at: datetime | None = None,
) -> RiskOut:
    data = load(db, [student.id], as_of)[0]
    try:
        result = compute_risk(to_risk_inputs(data), as_of=as_of)
    except RiskValidationError as exc:
        raise AppError("VALIDATION_ERROR", str(exc), 422) from exc
    if persist:
        _persist_if_needed(
            db, student.id, as_of, result, computed_at=computed_at
        )
    return _to_out(student.id, as_of, result)


def get_current(db: Session, student: Student, as_of: date) -> RiskOut:
    return compute_for_student(db, student, as_of)


def get_history(db: Session, student: Student) -> RiskHistoryOut:
    rows = db.execute(
        select(RiskAssessment)
        .where(RiskAssessment.student_id == student.id)
        .order_by(RiskAssessment.as_of.asc(), RiskAssessment.computed_at.asc())
    ).scalars().all()
    return RiskHistoryOut(
        student_id=student.id,
        items=[RiskHistoryItemOut.model_validate(row) for row in rows],
    )
