import pytest
from sqlalchemy.orm import Session
from tests.helpers import add_student, add_subject, add_teacher, assign_teacher, enroll

from app.api.deps import (
    authorize_student_access,
    authorize_teacher_subject_write,
    teacher_can_write_subject,
)
from app.core.errors import Forbidden, NotFound


def _reload_user(db: Session, user_id: int):
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    from app.models.user import User

    return db.execute(
        select(User)
        .options(selectinload(User.student), selectinload(User.teacher))
        .where(User.id == user_id)
    ).scalar_one()


def test_student_own_and_me(db_session: Session, demo_password_hash: str) -> None:
    user, student = add_student(
        db_session,
        password_hash=demo_password_hash,
        email="a@demo.edu",
        student_code="A001",
    )
    user = _reload_user(db_session, user.id)
    own = authorize_student_access(str(student.id), db_session, user)
    assert own.id == student.id
    me = authorize_student_access("me", db_session, user)
    assert me.id == student.id


def test_student_cannot_access_other(
    db_session: Session, demo_password_hash: str
) -> None:
    user_a, _student_a = add_student(
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
    user_a = _reload_user(db_session, user_a.id)
    with pytest.raises(Forbidden):
        authorize_student_access(str(student_b.id), db_session, user_a)


def test_teacher_visible_and_hidden(
    db_session: Session, demo_password_hash: str
) -> None:
    subject = add_subject(db_session, code="CS301", name="DSA")
    other = add_subject(db_session, code="CS304", name="DBMS")
    t_user, teacher = add_teacher(
        db_session, password_hash=demo_password_hash, email="t@demo.edu"
    )
    assign_teacher(db_session, teacher, subject, section="ALL")
    _sa_user, student_visible = add_student(
        db_session,
        password_hash=demo_password_hash,
        email="vis@demo.edu",
        student_code="V001",
        section="A",
    )
    _sb_user, student_hidden = add_student(
        db_session,
        password_hash=demo_password_hash,
        email="hid@demo.edu",
        student_code="H001",
        section="A",
    )
    enroll(db_session, student_visible, subject)
    enroll(db_session, student_hidden, other)
    t_user = _reload_user(db_session, t_user.id)

    seen = authorize_student_access(str(student_visible.id), db_session, t_user)
    assert seen.id == student_visible.id
    with pytest.raises(Forbidden):
        authorize_student_access(str(student_hidden.id), db_session, t_user)


def test_teacher_section_filter(db_session: Session, demo_password_hash: str) -> None:
    subject = add_subject(db_session, code="CS301", name="DSA")
    t_user, teacher = add_teacher(
        db_session, password_hash=demo_password_hash, email="t2@demo.edu"
    )
    assign_teacher(db_session, teacher, subject, section="B")
    _a_user, student_a = add_student(
        db_session,
        password_hash=demo_password_hash,
        email="seca@demo.edu",
        student_code="SA1",
        section="A",
    )
    _b_user, student_b = add_student(
        db_session,
        password_hash=demo_password_hash,
        email="secb@demo.edu",
        student_code="SB1",
        section="B",
    )
    enroll(db_session, student_a, subject)
    enroll(db_session, student_b, subject)
    t_user = _reload_user(db_session, t_user.id)

    seen = authorize_student_access(str(student_b.id), db_session, t_user)
    assert seen.id == student_b.id
    with pytest.raises(Forbidden):
        authorize_student_access(str(student_a.id), db_session, t_user)


def test_teacher_missing_student_is_404(
    db_session: Session, demo_password_hash: str
) -> None:
    t_user, _teacher = add_teacher(
        db_session, password_hash=demo_password_hash, email="t@demo.edu"
    )
    t_user = _reload_user(db_session, t_user.id)
    with pytest.raises(NotFound):
        authorize_student_access("9999", db_session, t_user)


def test_teacher_cannot_use_me(db_session: Session, demo_password_hash: str) -> None:
    t_user, _teacher = add_teacher(
        db_session, password_hash=demo_password_hash, email="t@demo.edu"
    )
    t_user = _reload_user(db_session, t_user.id)
    with pytest.raises(Forbidden):
        authorize_student_access("me", db_session, t_user)


def test_teacher_write_requires_assignment_and_section(
    db_session: Session, demo_password_hash: str
) -> None:
    t_user, teacher = add_teacher(
        db_session, password_hash=demo_password_hash, email="t@demo.edu"
    )
    _s_user, student_a = add_student(
        db_session,
        password_hash=demo_password_hash,
        email="a@demo.edu",
        student_code="A001",
        section="A",
    )
    _b_user, student_b = add_student(
        db_session,
        password_hash=demo_password_hash,
        email="b@demo.edu",
        student_code="B001",
        section="B",
    )
    subject = add_subject(db_session, code="CS301", name="DSA")
    assign_teacher(db_session, teacher, subject, section="A")
    t_user = _reload_user(db_session, t_user.id)

    assert teacher_can_write_subject(db_session, teacher.id, subject.id) is True
    assert (
        teacher_can_write_subject(db_session, teacher.id, subject.id, student_a) is True
    )
    assert (
        teacher_can_write_subject(
            db_session, teacher.id, subject.id, student_b
        )
        is False
    )
    authorize_teacher_subject_write(db_session, t_user, subject.id, student_a)
    with pytest.raises(Forbidden):
        authorize_teacher_subject_write(db_session, t_user, subject.id, student_b)
