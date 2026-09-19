import time
from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from tests.helpers import (
    add_assessment,
    add_attendance,
    add_student,
    add_study_habit,
    add_subject,
    add_teacher,
    assign_teacher,
    bearer,
    enroll,
)


def test_teacher_students_200_under_two_seconds_no_n_plus_one(
    auth_client: TestClient,
    db_session: Session,
    db_engine: Engine,
    demo_password_hash: str,
) -> None:
    _ut, teacher = add_teacher(
        db_session, password_hash=demo_password_hash, email="t@demo.edu"
    )
    subject = add_subject(db_session, code="CS301", name="DSA")
    assign_teacher(db_session, teacher, subject)
    as_of = date(2026, 9, 19)
    for index in range(200):
        _user, student = add_student(
            db_session,
            password_hash=demo_password_hash,
            email=f"s{index}@demo.edu",
            student_code=f"S{index:03d}",
            full_name=f"Student {index:03d}",
        )
        enrollment = enroll(db_session, student, subject)
        add_attendance(
            db_session,
            enrollment,
            record_date=as_of,
            classes_held=5,
            classes_attended=4,
        )
        add_assessment(
            db_session,
            enrollment,
            assessment_date=as_of,
            obtained_marks=7,
            max_marks=10,
        )
        add_study_habit(db_session, student)

    headers = bearer(auth_client, "t@demo.edu")
    statements: list[str] = []

    def _before_cursor(_conn, _cursor, statement, _params, _context, _executemany):
        statements.append(statement)

    event.listen(db_engine, "before_cursor_execute", _before_cursor)
    try:
        started = time.perf_counter()
        response = auth_client.get(
            f"/api/v1/teacher/students?as_of={as_of.isoformat()}&page_size=100",
            headers=headers,
        )
        elapsed = time.perf_counter() - started
    finally:
        event.remove(db_engine, "before_cursor_execute", _before_cursor)

    assert response.status_code == 200
    assert response.json()["total"] == 200
    assert elapsed < 2.0
    select_count = sum(
        1 for item in statements if item.lstrip().upper().startswith("SELECT")
    )
    assert select_count < 40
