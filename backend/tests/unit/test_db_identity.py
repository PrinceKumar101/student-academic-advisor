import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models import Student, Teacher, User, UserRole


def _user(
    session: Session,
    *,
    email: str = "student@demo.edu",
    role: UserRole = UserRole.STUDENT,
) -> User:
    user = User(email=email, password_hash=hash_password("Demo@1234"), role=role)
    session.add(user)
    session.flush()
    return user


def _student(
    session: Session,
    user: User,
    *,
    student_code: str = "CS2025001",
    semester: int = 5,
) -> Student:
    student = Student(
        user_id=user.id,
        student_code=student_code,
        full_name="Demo Student",
        department="CSE",
        semester=semester,
        section="A",
    )
    session.add(student)
    session.flush()
    return student


def test_create_all_builds_identity_tables(db_session: Session) -> None:
    user = _user(db_session)
    student = _student(db_session, user)
    teacher_user = _user(
        db_session, email="teacher@demo.edu", role=UserRole.TEACHER
    )
    teacher = Teacher(
        user_id=teacher_user.id, full_name="Demo Teacher", department="CSE"
    )
    db_session.add(teacher)
    db_session.flush()

    assert student.id is not None
    assert teacher.id is not None
    assert db_session.get(User, user.id) is not None


def test_fk_rejects_student_with_missing_user(db_session: Session) -> None:
    orphan = Student(
        user_id=9999,
        student_code="CS2025999",
        full_name="Missing User",
        department="CSE",
        semester=5,
        section="A",
    )
    db_session.add(orphan)
    with pytest.raises(IntegrityError):
        db_session.flush()


def test_unique_email_enforced(db_session: Session) -> None:
    _user(db_session, email="Same@Demo.edu")
    duplicate = User(
        email="same@demo.edu",
        password_hash=hash_password("other"),
        role=UserRole.STUDENT,
    )
    db_session.add(duplicate)
    with pytest.raises(IntegrityError):
        db_session.flush()


def test_unique_student_code_enforced(db_session: Session) -> None:
    first = _user(db_session, email="one@demo.edu")
    _student(db_session, first, student_code="CS2025001")
    second = _user(db_session, email="two@demo.edu")
    with pytest.raises(IntegrityError):
        _student(db_session, second, student_code="CS2025001")


def test_semester_check_rejects_zero_and_nine(db_session: Session) -> None:
    zero_user = _user(db_session, email="zero@demo.edu")
    with pytest.raises(IntegrityError):
        _student(db_session, zero_user, student_code="CS2025000", semester=0)
    db_session.rollback()

    nine_user = _user(db_session, email="nine@demo.edu")
    with pytest.raises(IntegrityError):
        _student(db_session, nine_user, student_code="CS2025009", semester=9)


def test_unique_user_id_on_student_profile(db_session: Session) -> None:
    user = _user(db_session)
    _student(db_session, user, student_code="CS2025001")
    with pytest.raises(IntegrityError):
        _student(db_session, user, student_code="CS2025002")


def test_hash_password_never_returns_plain() -> None:
    plain = "Demo@1234"
    hashed = hash_password(plain)
    assert hashed != plain
    assert plain not in hashed


def test_verify_password_true_and_false() -> None:
    hashed = hash_password("correct-horse")
    assert verify_password("correct-horse", hashed) is True
    assert verify_password("wrong-password", hashed) is False
