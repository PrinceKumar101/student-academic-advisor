from datetime import date

import pytest
from sqlalchemy import inspect
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.init import create_all, drop_all
from app.models import RiskAssessment, RiskLevel, Student, User, UserRole


def _student(session: Session) -> Student:
    user = User(
        email="risk-student@demo.edu",
        password_hash=hash_password("Demo@1234"),
        role=UserRole.STUDENT,
    )
    session.add(user)
    session.flush()
    student = Student(
        user_id=user.id,
        student_code="CS2025801",
        full_name="Risk Student",
        department="CSE",
        semester=5,
        section="A",
    )
    session.add(student)
    session.flush()
    return student


def _snapshot(
    session: Session,
    student: Student,
    *,
    score: float | None = 67.1,
    level: RiskLevel = RiskLevel.HIGH,
    components: dict | None = None,
    flags: list | None = None,
) -> RiskAssessment:
    row = RiskAssessment(
        student_id=student.id,
        as_of=date(2026, 9, 19),
        score=score,
        level=level,
        escalated=False,
        escalation_reason=None,
        data_completeness=1.0,
        config_version="1.0",
        components=components or {"attendance": {"risk": 65.0}},
        flags=flags or ["PARTIAL_DATA"],
    )
    session.add(row)
    session.flush()
    return row


def test_risk_assessment_stores_json_and_null_score(db_session: Session) -> None:
    student = _student(db_session)
    row = _snapshot(
        db_session,
        student,
        score=None,
        level=RiskLevel.INSUFFICIENT_DATA,
        components={"study_habits": {"risk": 12.5}},
        flags=["PARTIAL_DATA", "LOW_SAMPLE:internal"],
    )
    db_session.refresh(row)
    assert row.id is not None
    assert row.score is None
    assert row.level is RiskLevel.INSUFFICIENT_DATA
    assert row.components["study_habits"]["risk"] == 12.5
    assert row.flags == ["PARTIAL_DATA", "LOW_SAMPLE:internal"]
    assert student.risk_assessments[0].id == row.id


def test_risk_assessment_fk_rejects_missing_student(db_session: Session) -> None:
    orphan = RiskAssessment(
        student_id=9999,
        as_of=date(2026, 9, 19),
        score=1.3,
        level=RiskLevel.LOW,
        escalated=False,
        data_completeness=1.0,
        config_version="1.0",
        components={},
        flags=[],
    )
    db_session.add(orphan)
    with pytest.raises(IntegrityError):
        db_session.flush()


def test_risk_assessments_student_computed_at_index(db_engine: Engine) -> None:
    inspector = inspect(db_engine)
    indexes = inspector.get_indexes("risk_assessments")
    columns = {tuple(index["column_names"]) for index in indexes}
    assert ("student_id", "computed_at") in columns


def test_schema_indexes_present_for_existing_tables(db_engine: Engine) -> None:
    inspector = inspect(db_engine)
    enrollment_indexes = {
        tuple(index["column_names"]) for index in inspector.get_indexes("enrollments")
    }
    assert ("student_id",) in enrollment_indexes
    assert ("subject_id",) in enrollment_indexes

    assessment_indexes = {
        tuple(index["column_names"])
        for index in inspector.get_indexes("assessments")
    }
    assert ("enrollment_id", "type", "assessment_date") in assessment_indexes

    attendance_uniques = {
        tuple(constraint["column_names"])
        for constraint in inspector.get_unique_constraints("attendance_records")
    }
    assert ("enrollment_id", "record_date") in attendance_uniques


def test_drop_all_then_create_all_rebuilds_risk_table(db_engine: Engine) -> None:
    inspector = inspect(db_engine)
    assert "risk_assessments" in inspector.get_table_names()
    drop_all(db_engine)
    assert "risk_assessments" not in inspect(db_engine).get_table_names()
    create_all(db_engine)
    names = inspect(db_engine).get_table_names()
    assert "risk_assessments" in names
    assert "students" in names
