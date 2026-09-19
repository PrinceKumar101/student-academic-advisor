from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from tests.helpers import (
    add_assessment,
    add_attendance,
    add_student,
    add_subject,
    add_teacher,
    assign_teacher,
    bearer,
    enroll,
)

AS_OF = "2026-09-19"


def _world(db_session: Session, demo_password_hash: str):
    _ua, student_a = add_student(
        db_session,
        password_hash=demo_password_hash,
        email="a@demo.edu",
        student_code="A001",
        full_name="Ada Lovelace",
        department="CS",
        semester=5,
        section="A",
    )
    _ub, student_b = add_student(
        db_session,
        password_hash=demo_password_hash,
        email="b@demo.edu",
        student_code="B001",
        full_name="Bea Hopper",
        department="CS",
        semester=5,
        section="B",
    )
    _uc, student_c = add_student(
        db_session,
        password_hash=demo_password_hash,
        email="c@demo.edu",
        student_code="C001",
        full_name="Cara EE",
        department="EE",
        semester=3,
        section="A",
    )
    _ud, hidden = add_student(
        db_session,
        password_hash=demo_password_hash,
        email="d@demo.edu",
        student_code="D001",
        full_name="Hidden",
        department="CS",
        semester=5,
        section="A",
    )
    _ut, teacher = add_teacher(
        db_session, password_hash=demo_password_hash, email="t@demo.edu"
    )
    _uo, other = add_teacher(
        db_session, password_hash=demo_password_hash, email="other@demo.edu"
    )
    cs301 = add_subject(db_session, code="CS301", name="DSA")
    cs302 = add_subject(db_session, code="CS302", name="OS")
    enroll_a = enroll(db_session, student_a, cs301)
    enroll_b = enroll(db_session, student_b, cs301)
    enroll_c = enroll(db_session, student_c, cs301)
    enroll(db_session, hidden, cs302)
    assign_teacher(db_session, teacher, cs301)
    assign_teacher(db_session, other, cs302)
    add_attendance(
        db_session,
        enroll_a,
        record_date=date(2026, 9, 12),
        classes_held=10,
        classes_attended=8,
    )
    add_attendance(
        db_session,
        enroll_b,
        record_date=date(2026, 9, 12),
        classes_held=10,
        classes_attended=6,
    )
    add_attendance(
        db_session,
        enroll_c,
        record_date=date(2026, 9, 12),
        classes_held=10,
        classes_attended=10,
    )
    add_assessment(
        db_session,
        enroll_a,
        assessment_date=date(2026, 9, 10),
        name="Q1",
        max_marks=100,
        obtained_marks=50,
    )
    add_assessment(
        db_session,
        enroll_b,
        assessment_date=date(2026, 9, 10),
        name="Q1",
        max_marks=100,
        obtained_marks=70,
    )
    add_assessment(
        db_session,
        enroll_c,
        assessment_date=date(2026, 9, 10),
        name="Q1",
        max_marks=100,
        obtained_marks=90,
    )
    return student_a, student_b, student_c, hidden, cs301, cs302


def test_dashboard_hand_computed_means(
    auth_client: TestClient, db_session: Session, demo_password_hash: str
) -> None:
    _world(db_session, demo_password_hash)
    teacher = bearer(auth_client, "t@demo.edu")
    student = bearer(auth_client, "a@demo.edu")
    denied = auth_client.get("/api/v1/teacher/dashboard", headers=student)
    assert denied.status_code == 403

    response = auth_client.get(
        f"/api/v1/teacher/dashboard?as_of={AS_OF}", headers=teacher
    )
    assert response.status_code == 200
    body = response.json()
    assert body["group_size"] == 3
    assert body["mean_attendance"] == 80.0
    assert body["mean_marks"] == 70.0
    assert body["subject_performance"][0]["code"] == "CS301"
    assert body["subject_performance"][0]["mean_percent"] == 70.0
    assert set(body["risk_counts"]) == {
        "LOW",
        "MEDIUM",
        "HIGH",
        "INSUFFICIENT_DATA",
    }


def test_student_filters_and_empty(
    auth_client: TestClient, db_session: Session, demo_password_hash: str
) -> None:
    student_a, student_b, student_c, _hidden, cs301, cs302 = _world(
        db_session, demo_password_hash
    )
    teacher = bearer(auth_client, "t@demo.edu")
    other = bearer(auth_client, "other@demo.edu")

    all_visible = auth_client.get(
        f"/api/v1/teacher/students?as_of={AS_OF}&page_size=50",
        headers=teacher,
    )
    assert all_visible.status_code == 200
    ids = {item["id"] for item in all_visible.json()["items"]}
    assert ids == {student_a.id, student_b.id, student_c.id}

    by_dept = auth_client.get(
        f"/api/v1/teacher/students?department=EE&as_of={AS_OF}",
        headers=teacher,
    )
    assert [item["id"] for item in by_dept.json()["items"]] == [student_c.id]

    by_sem = auth_client.get(
        f"/api/v1/teacher/students?semester=5&as_of={AS_OF}",
        headers=teacher,
    )
    assert {item["id"] for item in by_sem.json()["items"]} == {
        student_a.id,
        student_b.id,
    }

    by_section = auth_client.get(
        f"/api/v1/teacher/students?section=B&as_of={AS_OF}",
        headers=teacher,
    )
    assert [item["id"] for item in by_section.json()["items"]] == [student_b.id]

    by_subject = auth_client.get(
        f"/api/v1/teacher/students?subject_id={cs301.id}&as_of={AS_OF}",
        headers=teacher,
    )
    assert by_subject.json()["total"] == 3

    search = auth_client.get(
        f"/api/v1/teacher/students?search=Lovelace&as_of={AS_OF}",
        headers=teacher,
    )
    assert [item["id"] for item in search.json()["items"]] == [student_a.id]

    combined = auth_client.get(
        "/api/v1/teacher/students"
        f"?department=CS&semester=5&section=A&subject_id={cs301.id}"
        f"&search=Ada&as_of={AS_OF}",
        headers=teacher,
    )
    assert [item["id"] for item in combined.json()["items"]] == [student_a.id]

    empty = auth_client.get(
        f"/api/v1/teacher/students?department=ME&as_of={AS_OF}",
        headers=teacher,
    )
    assert empty.json()["total"] == 0
    assert empty.json()["items"] == []

    other_subject = auth_client.get(
        f"/api/v1/teacher/students?subject_id={cs302.id}",
        headers=teacher,
    )
    assert other_subject.status_code == 403

    other_list = auth_client.get("/api/v1/teacher/students", headers=other)
    assert [item["student_code"] for item in other_list.json()["items"]] == [
        "D001"
    ]


def test_risk_level_filter_and_subject_analytics(
    auth_client: TestClient, db_session: Session, demo_password_hash: str
) -> None:
    _student_a, _student_b, _student_c, _hidden, cs301, cs302 = _world(
        db_session, demo_password_hash
    )
    teacher = bearer(auth_client, "t@demo.edu")
    listing = auth_client.get(
        f"/api/v1/teacher/students?as_of={AS_OF}&page_size=50",
        headers=teacher,
    )
    levels = {item["risk_level"] for item in listing.json()["items"]}
    sample_level = next(iter(levels))
    filtered = auth_client.get(
        f"/api/v1/teacher/students?risk_level={sample_level}&as_of={AS_OF}",
        headers=teacher,
    )
    assert filtered.status_code == 200
    assert filtered.json()["items"]
    assert all(
        item["risk_level"] == sample_level for item in filtered.json()["items"]
    )

    analytics = auth_client.get(
        f"/api/v1/teacher/subjects/{cs301.id}/analytics?as_of={AS_OF}",
        headers=teacher,
    )
    assert analytics.status_code == 200
    body = analytics.json()
    assert body["code"] == "CS301"
    assert body["group_size"] == 3
    assert body["mean_attendance"] == 80.0

    hidden_subject = auth_client.get(
        f"/api/v1/teacher/subjects/{cs302.id}/analytics",
        headers=teacher,
    )
    assert hidden_subject.status_code == 403
