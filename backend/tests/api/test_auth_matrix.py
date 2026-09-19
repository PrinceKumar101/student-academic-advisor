from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from tests.helpers import (
    add_assessment,
    add_attendance,
    add_semester_result,
    add_student,
    add_study_habit,
    add_subject,
    add_teacher,
    assign_teacher,
    bearer,
    enroll,
)

AS_OF = "2026-09-19"


def _setup(db_session: Session, demo_password_hash: str) -> dict:
    _ua, student_a = add_student(
        db_session,
        password_hash=demo_password_hash,
        email="a@demo.edu",
        student_code="A001",
        full_name="Ada",
        section="A",
    )
    _ub, student_b = add_student(
        db_session,
        password_hash=demo_password_hash,
        email="b@demo.edu",
        student_code="B001",
        section="A",
    )
    _ut, teacher = add_teacher(
        db_session, password_hash=demo_password_hash, email="t@demo.edu"
    )
    _uo, other = add_teacher(
        db_session, password_hash=demo_password_hash, email="other@demo.edu"
    )
    subject = add_subject(db_session, code="CS301", name="DSA")
    other_subject = add_subject(db_session, code="CS302", name="OS")
    enrollment = enroll(db_session, student_a, subject)
    enroll(db_session, student_b, other_subject)
    assign_teacher(db_session, teacher, subject)
    assign_teacher(db_session, other, other_subject)
    add_study_habit(db_session, student_a)
    add_semester_result(db_session, student_a, semester=4, percentage=70.0)
    attendance = add_attendance(
        db_session,
        enrollment,
        record_date=date(2026, 9, 12),
        classes_held=10,
        classes_attended=6,
    )
    assessment = add_assessment(
        db_session,
        enrollment,
        assessment_date=date(2026, 9, 10),
        obtained_marks=4,
        max_marks=10,
    )
    return {
        "a": student_a.id,
        "b": student_b.id,
        "subject": subject.id,
        "attendance": attendance.id,
        "assessment": assessment.id,
    }


def _tokens(client: TestClient) -> dict[str, dict[str, str] | None]:
    return {
        "anon": None,
        "self": bearer(client, "a@demo.edu"),
        "other": bearer(client, "b@demo.edu"),
        "teacher": bearer(client, "t@demo.edu"),
        "other_teacher": bearer(client, "other@demo.edu"),
    }


def _expect(anon: int, self: int, other: int, teacher: int, other_teacher: int):
    return {
        "anon": anon,
        "self": self,
        "other": other,
        "teacher": teacher,
        "other_teacher": other_teacher,
    }


def _cases(ids: dict) -> list[tuple]:
    a = ids["a"]
    sid = ids["subject"]
    att = ids["attendance"]
    ass = ids["assessment"]
    exam = (date.today() + timedelta(days=14)).isoformat()
    csv_bytes = (
        b"student_code,subject_code,record_date,classes_held,classes_attended\n"
        b"A001,CS301,2026-09-05,5,4\n"
    )
    return [
        ("health", "GET", "/api/v1/health", None, None, None, _expect(200, 200, 200, 200, 200)),
        ("me", "GET", "/api/v1/auth/me", None, None, None, _expect(401, 200, 200, 200, 200)),
        ("logout", "POST", "/api/v1/auth/logout", None, None, None, _expect(401, 204, 204, 204, 204)),
        ("profile", "GET", f"/api/v1/students/{a}", None, None, None, _expect(401, 200, 403, 200, 403)),
        ("overview", "GET", f"/api/v1/students/{a}/overview?as_of={AS_OF}", None, None, None, _expect(401, 200, 403, 200, 403)),
        ("habits_get", "GET", f"/api/v1/students/{a}/study-habits", None, None, None, _expect(401, 200, 403, 200, 403)),
        (
            "habits_put",
            "PUT",
            f"/api/v1/students/{a}/study-habits",
            {"study_hours_per_day": 2, "self_confidence": 3, "available_hours_per_day": 3},
            None,
            None,
            _expect(401, 200, 403, 403, 403),
        ),
        ("results", "GET", f"/api/v1/students/{a}/semester-results", None, None, None, _expect(401, 200, 403, 200, 403)),
        (
            "results_put",
            "PUT",
            f"/api/v1/students/{a}/semester-results/3",
            {"percentage": 71, "sgpa": 7.1},
            None,
            None,
            _expect(401, 403, 403, 200, 403),
        ),
        ("subjects", "GET", "/api/v1/subjects", None, None, None, _expect(401, 200, 200, 200, 200)),
        (
            "subjects_post",
            "POST",
            "/api/v1/subjects",
            {"code": "CS399", "name": "New", "semester": 5},
            None,
            None,
            _expect(401, 403, 403, 201, 201),
        ),
        (
            "subjects_patch",
            "PATCH",
            f"/api/v1/subjects/{sid}",
            {"name": "DSA Updated"},
            None,
            None,
            _expect(401, 403, 403, 200, 403),
        ),
        (
            "enroll_post",
            "POST",
            f"/api/v1/subjects/{sid}/enrollments",
            {"student_id": ids["b"]},
            None,
            None,
            _expect(401, 403, 403, 201, 403),
        ),
        ("attendance_get", "GET", f"/api/v1/attendance?student_id={a}", None, None, None, _expect(401, 200, 403, 200, 403)),
        (
            "attendance_post",
            "POST",
            "/api/v1/attendance",
            {
                "student_id": a,
                "subject_id": sid,
                "record_date": "2026-09-05",
                "classes_held": 5,
                "classes_attended": 4,
            },
            None,
            None,
            _expect(401, 403, 403, 201, 403),
        ),
        (
            "attendance_put",
            "PUT",
            f"/api/v1/attendance/{att}",
            {"classes_held": 10, "classes_attended": 7},
            None,
            None,
            _expect(401, 403, 403, 200, 403),
        ),
        ("attendance_del", "DELETE", f"/api/v1/attendance/{att}", None, None, None, _expect(401, 403, 403, 204, 403)),
        ("assess_get", "GET", f"/api/v1/assessments?student_id={a}", None, None, None, _expect(401, 200, 403, 200, 403)),
        (
            "assess_post",
            "POST",
            "/api/v1/assessments",
            {
                "student_id": a,
                "subject_id": sid,
                "type": "QUIZ",
                "name": "Extra",
                "max_marks": 10,
                "obtained_marks": 8,
                "status": "GRADED",
                "assessment_date": "2026-09-08",
            },
            None,
            None,
            _expect(401, 403, 403, 201, 403),
        ),
        (
            "assess_put",
            "PUT",
            f"/api/v1/assessments/{ass}",
            {"obtained_marks": 5},
            None,
            None,
            _expect(401, 403, 403, 200, 403),
        ),
        ("assess_del", "DELETE", f"/api/v1/assessments/{ass}", None, None, None, _expect(401, 403, 403, 204, 403)),
        ("risk", "GET", f"/api/v1/risk/{a}?as_of={AS_OF}", None, None, None, _expect(401, 200, 403, 200, 403)),
        ("risk_hist", "GET", f"/api/v1/risk/{a}/history", None, None, None, _expect(401, 200, 403, 200, 403)),
        (
            "whatif",
            "POST",
            f"/api/v1/risk/{a}/what-if?as_of={AS_OF}",
            {"overrides": {"attendance_percent": 80}},
            None,
            None,
            _expect(401, 200, 403, 200, 403),
        ),
        ("trends", "GET", f"/api/v1/trends/{a}?as_of={AS_OF}", None, None, None, _expect(401, 200, 403, 200, 403)),
        ("warnings", "GET", f"/api/v1/trends/{a}/warnings?as_of={AS_OF}", None, None, None, _expect(401, 200, 403, 200, 403)),
        ("subjects_an", "GET", f"/api/v1/analytics/students/{a}/subjects?as_of={AS_OF}", None, None, None, _expect(401, 200, 403, 200, 403)),
        ("compare", "GET", f"/api/v1/analytics/students/{a}/comparison?as_of={AS_OF}", None, None, None, _expect(401, 200, 403, 200, 403)),
        ("ai_usage", "GET", "/api/v1/ai/usage", None, None, None, _expect(401, 200, 200, 200, 200)),
        (
            "ai_analysis",
            "POST",
            "/api/v1/ai/analysis",
            {"student_id": str(a)},
            None,
            None,
            _expect(401, 200, 403, 200, 403),
        ),
        (
            "ai_chat",
            "POST",
            "/api/v1/ai/chat",
            {"question": "Why is my attendance low?"},
            None,
            None,
            _expect(401, 200, 200, 403, 403),
        ),
        ("chat_hist", "GET", "/api/v1/ai/chat/history", None, None, None, _expect(401, 200, 200, 403, 403)),
        ("chat_clear", "DELETE", "/api/v1/ai/chat/history", None, None, None, _expect(401, 204, 204, 403, 403)),
        (
            "ai_suggest",
            "POST",
            "/api/v1/ai/intervention-suggestions",
            {"student_id": str(a)},
            None,
            None,
            _expect(401, 403, 403, 200, 403),
        ),
        ("plans_list", "GET", "/api/v1/study-plans", None, None, None, _expect(401, 200, 200, 403, 403)),
        (
            "plans_post",
            "POST",
            "/api/v1/study-plans",
            {"exam_date": exam, "available_hours_per_day": 3, "subject_ids": []},
            None,
            None,
            _expect(401, 200, 200, 403, 403),
        ),
        ("interventions_list", "GET", "/api/v1/interventions", None, None, None, _expect(401, 200, 200, 200, 200)),
        (
            "interventions_post",
            "POST",
            f"/api/v1/interventions?as_of={AS_OF}",
            {"student_id": a, "title": "Help"},
            None,
            None,
            _expect(401, 403, 403, 201, 403),
        ),
        ("teacher_dash", "GET", f"/api/v1/teacher/dashboard?as_of={AS_OF}", None, None, None, _expect(401, 403, 403, 200, 200)),
        ("teacher_students", "GET", f"/api/v1/teacher/students?as_of={AS_OF}", None, None, None, _expect(401, 403, 403, 200, 200)),
        (
            "teacher_analytics",
            "GET",
            f"/api/v1/teacher/subjects/{sid}/analytics?as_of={AS_OF}",
            None,
            None,
            None,
            _expect(401, 403, 403, 200, 403),
        ),
        (
            "import_att",
            "POST",
            "/api/v1/imports/attendance?dry_run=true",
            None,
            None,
            ("file.csv", csv_bytes, "text/csv"),
            _expect(401, 403, 403, 200, 200),
        ),
    ]


@pytest.mark.parametrize("actor", ["anon", "self", "other", "teacher", "other_teacher"])
def test_authorization_matrix(
    auth_client: TestClient,
    db_session: Session,
    demo_password_hash: str,
    actor: str,
) -> None:
    ids = _setup(db_session, demo_password_hash)
    headers = _tokens(auth_client)[actor]
    teacher = bearer(auth_client, "t@demo.edu")
    created = auth_client.post(
        f"/api/v1/interventions?as_of={AS_OF}",
        headers=teacher,
        json={"student_id": ids["a"], "title": "Existing"},
    )
    assert created.status_code == 201
    intervention_id = created.json()["id"]

    extra = [
        (
            "intervention_get",
            "GET",
            f"/api/v1/interventions/{intervention_id}",
            None,
            None,
            None,
            _expect(401, 200, 403, 200, 403),
        ),
        (
            "intervention_progress",
            "GET",
            f"/api/v1/interventions/{intervention_id}/progress?as_of={AS_OF}",
            None,
            None,
            None,
            _expect(401, 200, 403, 200, 403),
        ),
        (
            "intervention_patch",
            "PATCH",
            f"/api/v1/interventions/{intervention_id}",
            {"status": "IN_PROGRESS"},
            None,
            None,
            _expect(401, 200, 403, 200, 403),
        ),
    ]

    failures: list[str] = []
    for name, method, path, json_body, _form, upload, expected in _cases(ids) + extra:
        kwargs: dict = {}
        if headers:
            kwargs["headers"] = headers
        if json_body is not None:
            kwargs["json"] = json_body
        if upload is not None:
            filename, content, content_type = upload
            kwargs["files"] = {"file": (filename, content, content_type)}
        response = auth_client.request(method, path, **kwargs)
        want = expected[actor]
        if response.status_code != want:
            failures.append(
                f"{name}/{actor}: {path} -> {response.status_code} (want {want}) {response.text[:200]}"
            )
    assert not failures, "\n".join(failures)
