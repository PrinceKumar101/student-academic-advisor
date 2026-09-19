from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from tests.helpers import add_student, add_subject, add_teacher, assign_teacher, enroll

from app.core.security import create_access_token
from app.schemas.auth import LOGIN_FAILURE_MESSAGE

REGISTER_BODY = {
    "email": "new@demo.edu",
    "password": "Strong#12",
    "full_name": "New Student",
    "student_code": "NEW001",
    "department": "CS",
    "semester": 5,
    "section": "A",
}


def _login(client: TestClient, email: str, password: str = "Demo@1234"):
    return client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )


def test_register_and_login(auth_client: TestClient) -> None:
    created = auth_client.post("/api/v1/auth/register", json=REGISTER_BODY)
    assert created.status_code == 201
    body = created.json()
    assert set(body.keys()) == {"user_id", "student_id"}
    assert "password" not in body
    assert "password_hash" not in created.text

    login = _login(auth_client, REGISTER_BODY["email"], REGISTER_BODY["password"])
    assert login.status_code == 200
    payload = login.json()
    assert payload["token_type"] == "bearer"
    assert payload["expires_in"] == 3600
    assert payload["user"]["role"] == "STUDENT"
    assert payload["user"]["student_id"] == body["student_id"]
    assert payload["user"]["full_name"] == "New Student"
    assert "password_hash" not in login.text

    me = auth_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {payload['access_token']}"},
    )
    assert me.status_code == 200
    assert me.json()["email"] == "new@demo.edu"
    assert me.json()["student_id"] == body["student_id"]
    assert "password_hash" not in me.text

    logout = auth_client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {payload['access_token']}"},
    )
    assert logout.status_code == 204
    assert logout.content == b""


def test_register_ignores_role_field(auth_client: TestClient) -> None:
    body = {**REGISTER_BODY, "role": "TEACHER"}
    created = auth_client.post("/api/v1/auth/register", json=body)
    assert created.status_code == 201
    login = _login(auth_client, body["email"], body["password"])
    assert login.json()["user"]["role"] == "STUDENT"
    assert login.json()["user"]["teacher_id"] is None


def test_register_duplicate_email_and_code(
    auth_client: TestClient, db_session: Session, demo_password_hash: str
) -> None:
    add_student(
        db_session,
        password_hash=demo_password_hash,
        email="taken@demo.edu",
        student_code="TAKEN1",
    )
    dup_email = {**REGISTER_BODY, "email": "taken@demo.edu"}
    assert auth_client.post("/api/v1/auth/register", json=dup_email).status_code == 409
    dup_code = {**REGISTER_BODY, "email": "other@demo.edu", "student_code": "TAKEN1"}
    assert auth_client.post("/api/v1/auth/register", json=dup_code).status_code == 409


def test_register_short_password(auth_client: TestClient) -> None:
    body = {**REGISTER_BODY, "password": "short"}
    response = auth_client.post("/api/v1/auth/register", json=body)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_login_failures_are_indistinguishable(
    auth_client: TestClient, db_session: Session, demo_password_hash: str
) -> None:
    add_student(
        db_session,
        password_hash=demo_password_hash,
        email="known@demo.edu",
        student_code="K001",
    )
    unknown = _login(auth_client, "missing@demo.edu", "Demo@1234")
    wrong = _login(auth_client, "known@demo.edu", "WrongPass1")
    assert unknown.status_code == 401
    assert wrong.status_code == 401
    assert unknown.json() == wrong.json()
    assert unknown.json()["error"]["code"] == "UNAUTHENTICATED"
    assert unknown.json()["error"]["message"] == LOGIN_FAILURE_MESSAGE


def test_inactive_user_rejected(
    auth_client: TestClient, db_session: Session, demo_password_hash: str
) -> None:
    user, _student = add_student(
        db_session,
        password_hash=demo_password_hash,
        email="sleep@demo.edu",
        student_code="Z001",
        is_active=False,
    )
    login = _login(auth_client, "sleep@demo.edu")
    assert login.status_code == 401
    assert login.json()["error"]["message"] == LOGIN_FAILURE_MESSAGE

    token = create_access_token(user_id=user.id, role="STUDENT")
    me = auth_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me.status_code == 401


def test_missing_expired_tampered_token(
    auth_client: TestClient, db_session: Session, demo_password_hash: str
) -> None:
    user, _student = add_student(
        db_session,
        password_hash=demo_password_hash,
        email="tok@demo.edu",
        student_code="T001",
    )
    missing = auth_client.get("/api/v1/auth/me")
    assert missing.status_code == 401
    assert missing.json()["error"]["code"] == "UNAUTHENTICATED"

    expired = create_access_token(
        user_id=user.id,
        role="STUDENT",
        now=datetime.now(UTC) - timedelta(hours=2),
        expires_minutes=1,
    )
    expired_resp = auth_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {expired}"},
    )
    assert expired_resp.status_code == 401

    good = create_access_token(user_id=user.id, role="STUDENT")
    tampered = good[:-2] + ("A" if good[-2] != "A" else "B") + good[-1]
    tampered_resp = auth_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tampered}"},
    )
    assert tampered_resp.status_code == 401


def test_student_forbidden_on_teacher_route_and_other_student(
    auth_client: TestClient, db_session: Session, demo_password_hash: str
) -> None:
    user_a, student_a = add_student(
        db_session,
        password_hash=demo_password_hash,
        email="a@demo.edu",
        student_code="A001",
    )
    _user_b, student_b = add_student(
        db_session,
        password_hash=demo_password_hash,
        email="b@demo.edu",
        student_code="B001",
    )
    token = create_access_token(user_id=user_a.id, role="STUDENT")
    headers = {"Authorization": f"Bearer {token}"}

    teacher_only = auth_client.get("/api/v1/_test/teacher-only", headers=headers)
    assert teacher_only.status_code == 403
    assert teacher_only.json()["error"]["code"] == "FORBIDDEN"

    other = auth_client.get(f"/api/v1/_test/students/{student_b.id}", headers=headers)
    assert other.status_code == 403

    own = auth_client.get(f"/api/v1/_test/students/{student_a.id}", headers=headers)
    assert own.status_code == 200
    assert own.json() == {"student_id": student_a.id}

    me = auth_client.get("/api/v1/_test/students/me", headers=headers)
    assert me.status_code == 200
    assert me.json() == {"student_id": student_a.id}


def test_teacher_visibility_matrix(
    auth_client: TestClient, db_session: Session, demo_password_hash: str
) -> None:
    subject = add_subject(db_session, code="CS301", name="DSA")
    other = add_subject(db_session, code="CS304", name="DBMS")
    t_user, teacher = add_teacher(
        db_session, password_hash=demo_password_hash, email="teach@demo.edu"
    )
    assign_teacher(db_session, teacher, subject, section="ALL")
    _vis_user, visible = add_student(
        db_session,
        password_hash=demo_password_hash,
        email="vis@demo.edu",
        student_code="V001",
    )
    _hid_user, hidden = add_student(
        db_session,
        password_hash=demo_password_hash,
        email="hid@demo.edu",
        student_code="H001",
    )
    enroll(db_session, visible, subject)
    enroll(db_session, hidden, other)

    login = _login(auth_client, "teach@demo.edu")
    assert login.status_code == 200
    assert login.json()["user"]["role"] == "TEACHER"
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    assert (
        auth_client.get(
            f"/api/v1/_test/students/{visible.id}", headers=headers
        ).status_code
        == 200
    )
    hidden_resp = auth_client.get(
        f"/api/v1/_test/students/{hidden.id}", headers=headers
    )
    assert hidden_resp.status_code == 403
    teacher_only = auth_client.get("/api/v1/_test/teacher-only", headers=headers)
    assert teacher_only.status_code == 200
