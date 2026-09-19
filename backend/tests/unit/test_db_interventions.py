from datetime import UTC, datetime

from sqlalchemy.orm import Session
from tests.helpers import add_student, add_teacher

from app.core.security import hash_password
from app.models.enums import InterventionStatus, Priority, RiskLevel
from app.models.intervention import Intervention


def test_intervention_persists_baseline(db_session: Session) -> None:
    password = hash_password("Demo@1234")
    _user, student = add_student(
        db_session,
        password_hash=password,
        email="s@demo.edu",
        student_code="S001",
    )
    _tu, teacher = add_teacher(
        db_session, password_hash=password, email="t@demo.edu"
    )
    created = datetime(2026, 9, 1, tzinfo=UTC)
    row = Intervention(
        student_id=student.id,
        teacher_id=teacher.id,
        title="Attendance plan",
        priority=Priority.HIGH,
        status=InterventionStatus.PENDING,
        baseline_score=84.0,
        baseline_level=RiskLevel.HIGH,
        baseline_at=created,
        created_at=created,
        updated_at=created,
    )
    db_session.add(row)
    db_session.commit()
    db_session.refresh(row)
    assert row.id is not None
    assert row.baseline_score == 84.0
    assert row.outcome_score is None
    assert row.subject_id is None
