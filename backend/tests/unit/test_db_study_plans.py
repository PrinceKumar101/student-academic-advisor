from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models import (
    Source,
    Student,
    StudyPlan,
    StudyPlanItem,
    Subject,
    User,
    UserRole,
)
from app.models.enums import Priority


def _student(session: Session) -> Student:
    user = User(
        email="planner@demo.edu",
        password_hash=hash_password("Demo@1234"),
        role=UserRole.STUDENT,
    )
    session.add(user)
    session.flush()
    student = Student(
        user_id=user.id,
        student_code="PL001",
        full_name="Planner",
        department="CS",
        semester=5,
        section="A",
    )
    session.add(student)
    session.flush()
    return student


def _subject(session: Session) -> Subject:
    subject = Subject(code="CS301", name="DSA", semester=5)
    session.add(subject)
    session.flush()
    return subject


def test_duration_check_and_cascade(db_session: Session) -> None:
    student = _student(db_session)
    subject = _subject(db_session)
    plan = StudyPlan(
        student_id=student.id,
        exam_date=date(2026, 10, 1),
        available_hours_per_day=3,
        inputs={"tips": []},
        source=Source.FALLBACK,
        prompt_version="plan_v1",
        created_by_user_id=student.user_id,
    )
    db_session.add(plan)
    db_session.flush()
    item = StudyPlanItem(
        plan_id=plan.id,
        plan_date=date(2026, 9, 20),
        subject_id=subject.id,
        topic="Trees",
        activity="Revise",
        duration_minutes=60,
        priority=Priority.HIGH,
    )
    db_session.add(item)
    db_session.commit()

    bad = StudyPlanItem(
        plan_id=plan.id,
        plan_date=date(2026, 9, 21),
        subject_id=subject.id,
        topic="Graphs",
        activity="Revise",
        duration_minutes=0,
        priority=Priority.LOW,
    )
    db_session.add(bad)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    db_session.delete(plan)
    db_session.commit()
    assert db_session.get(StudyPlanItem, item.id) is None
