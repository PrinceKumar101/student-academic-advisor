from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session
from tests.helpers import (
    add_assessment,
    add_attendance,
    add_student,
    add_subject,
    enroll,
)

from app.models.enums import AssessmentType
from app.models.risk_assessment import RiskAssessment
from app.services.risk_service import get_current


def test_snapshot_persists_once_for_same_score(
    db_session: Session, demo_password_hash: str
) -> None:
    _user, student = add_student(
        db_session,
        password_hash=demo_password_hash,
        email="a@demo.edu",
        student_code="A001",
    )
    subject = add_subject(db_session, code="CS301", name="DSA")
    enrollment = enroll(db_session, student, subject)
    add_attendance(
        db_session,
        enrollment,
        record_date=date(2026, 9, 12),
        classes_held=10,
        classes_attended=9,
    )
    add_assessment(
        db_session,
        enrollment,
        assessment_date=date(2026, 9, 10),
        name="Internal 1",
        assessment_type=AssessmentType.INTERNAL,
        max_marks=30,
        obtained_marks=24,
    )

    as_of = date(2026, 9, 19)
    first = get_current(db_session, student, as_of)
    second = get_current(db_session, student, as_of)
    assert first.score == second.score
    count = db_session.scalar(
        select(func.count())
        .select_from(RiskAssessment)
        .where(RiskAssessment.student_id == student.id)
    )
    assert count == 1

    add_attendance(
        db_session,
        enrollment,
        record_date=date(2026, 9, 19),
        classes_held=10,
        classes_attended=2,
    )
    changed = get_current(db_session, student, as_of)
    assert changed.score != first.score
    count = db_session.scalar(
        select(func.count())
        .select_from(RiskAssessment)
        .where(RiskAssessment.student_id == student.id)
    )
    assert count == 2
