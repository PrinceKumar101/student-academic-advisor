from sqlalchemy import inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models import AIChatMessage, ChatMessageRole, Student, User, UserRole


def test_chat_index_and_insert(db_engine: Engine, db_session: Session) -> None:
    inspector = inspect(db_engine)
    assert "ai_chat_messages" in inspector.get_table_names()
    indexes = {
        tuple(index["column_names"])
        for index in inspector.get_indexes("ai_chat_messages")
    }
    assert ("student_id", "created_at") in indexes

    user = User(
        email="chat@demo.edu",
        password_hash=hash_password("Demo@1234"),
        role=UserRole.STUDENT,
    )
    db_session.add(user)
    db_session.flush()
    student = Student(
        user_id=user.id,
        student_code="CH001",
        full_name="Chat Student",
        department="CS",
        semester=5,
        section="A",
    )
    db_session.add(student)
    db_session.flush()
    row = AIChatMessage(
        student_id=student.id,
        role=ChatMessageRole.USER,
        content="Why is my risk high?",
        source=None,
    )
    db_session.add(row)
    db_session.commit()
    assert row.id is not None
