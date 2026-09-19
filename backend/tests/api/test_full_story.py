from datetime import date, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from tests.helpers import bearer

from scripts.demo_advance import ADVANCE_WEEKS, advance_as_of, advance_student
from scripts.seed_generator import DEFAULT_AS_OF, RAHUL_EMAIL, seed_demo


def test_full_demo_story_with_ai_disabled(
    auth_client: TestClient, db_session: Session
) -> None:
    seed_demo(db_session, as_of=DEFAULT_AS_OF)
    db_session.commit()
    as_of = DEFAULT_AS_OF.isoformat()
    later = advance_as_of(DEFAULT_AS_OF, ADVANCE_WEEKS)

    rahul = bearer(auth_client, RAHUL_EMAIL)
    risk = auth_client.get(f"/api/v1/risk/me?as_of={as_of}", headers=rahul)
    assert risk.status_code == 200
    assert risk.json()["level"] == "HIGH"
    assert risk.json()["score"] >= 80

    trends = auth_client.get(f"/api/v1/trends/me?as_of={as_of}", headers=rahul)
    assert trends.status_code == 200
    assert trends.json()["attendance"]["label"] == "DECLINING"

    whatif = auth_client.post(
        f"/api/v1/risk/me/what-if?as_of={as_of}",
        headers=rahul,
        json={"overrides": {"attendance_percent": 80, "internal_percent": 60}},
    )
    assert whatif.status_code == 200
    assert whatif.json()["persisted"] is False
    assert whatif.json()["difference"] is not None

    analysis = auth_client.post(
        "/api/v1/ai/analysis", headers=rahul, json={"student_id": "me"}
    )
    assert analysis.status_code == 200
    assert analysis.json()["source"] == "FALLBACK"

    plan = auth_client.post(
        "/api/v1/study-plans",
        headers=rahul,
        json={
            "exam_date": (date.today() + timedelta(days=21)).isoformat(),
            "available_hours_per_day": 3,
            "subject_ids": [],
        },
    )
    assert plan.status_code == 200
    assert plan.json()["items"]

    teacher = bearer(auth_client, "teacher1@demo.edu")
    listed = auth_client.get(
        f"/api/v1/teacher/students?risk_level=HIGH&search=Rahul&as_of={as_of}",
        headers=teacher,
    )
    assert listed.status_code == 200
    assert listed.json()["total"] >= 1

    student_id = risk.json()["student_id"]
    created = auth_client.post(
        f"/api/v1/interventions?as_of={as_of}",
        headers=teacher,
        json={"student_id": student_id, "title": "Attendance recovery plan"},
    )
    assert created.status_code == 201
    assert created.json()["baseline_level"] == "HIGH"

    from app.models.student import Student

    student = db_session.get(Student, student_id)
    assert student is not None
    advance_student(db_session, student, as_of=DEFAULT_AS_OF, weeks=ADVANCE_WEEKS)
    db_session.commit()

    progress = auth_client.get(
        f"/api/v1/interventions/{created.json()['id']}/progress?as_of={later.isoformat()}",
        headers=teacher,
    )
    assert progress.status_code == 200
    body = progress.json()
    assert body["direction"] == "IMPROVED"
    assert body["current"]["score"] is not None
    assert 50 <= body["current"]["score"] <= 70
