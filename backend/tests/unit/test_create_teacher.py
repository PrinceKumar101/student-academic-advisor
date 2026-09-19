import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import Conflict
from app.models.enums import UserRole
from app.models.user import User
from app.services.auth_service import create_teacher_account


def test_create_teacher_account(db_session: Session) -> None:
    teacher = create_teacher_account(
        db_session,
        email="Prof@Demo.edu",
        password="Teach#123",
        full_name="Prof Demo",
        department="CS",
    )
    user = db_session.execute(
        select(User).where(User.id == teacher.user_id)
    ).scalar_one()
    assert user.email == "prof@demo.edu"
    assert user.role == UserRole.TEACHER
    assert teacher.full_name == "Prof Demo"
    assert "Teach#123" not in user.password_hash


def test_create_teacher_duplicate_email(db_session: Session) -> None:
    create_teacher_account(
        db_session,
        email="prof@demo.edu",
        password="Teach#123",
        full_name="Prof Demo",
        department="CS",
    )
    with pytest.raises(Conflict):
        create_teacher_account(
            db_session,
            email="prof@demo.edu",
            password="Teach#123",
            full_name="Other",
            department="CS",
        )
