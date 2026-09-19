from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models import (
    Assessment,
    AssessmentStatus,
    AssessmentType,
    AttendanceRecord,
    Enrollment,
    Student,
    StudyHabit,
    Subject,
    Teacher,
    TeachingAssignment,
    User,
    UserRole,
)


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


def _student(session: Session, user: User | None = None) -> Student:
    if user is None:
        user = _user(session)
    student = Student(
        user_id=user.id,
        student_code="CS2025001",
        full_name="Demo Student",
        department="CSE",
        semester=5,
        section="A",
    )
    session.add(student)
    session.flush()
    return student


def _teacher(session: Session) -> Teacher:
    user = _user(session, email="teacher@demo.edu", role=UserRole.TEACHER)
    teacher = Teacher(user_id=user.id, full_name="Demo Teacher", department="CSE")
    session.add(teacher)
    session.flush()
    return teacher


def _subject(session: Session, *, code: str = "CS301") -> Subject:
    subject = Subject(code=code, name="Operating Systems", semester=5)
    session.add(subject)
    session.flush()
    return subject


def _enrollment(
    session: Session,
    student: Student | None = None,
    subject: Subject | None = None,
) -> Enrollment:
    if student is None:
        student = _student(session)
    if subject is None:
        subject = _subject(session)
    enrollment = Enrollment(student_id=student.id, subject_id=subject.id)
    session.add(enrollment)
    session.flush()
    return enrollment


def _attendance(
    session: Session,
    enrollment: Enrollment,
    *,
    record_date: date = date(2026, 1, 5),
    classes_held: int = 5,
    classes_attended: int = 4,
) -> AttendanceRecord:
    record = AttendanceRecord(
        enrollment_id=enrollment.id,
        record_date=record_date,
        classes_held=classes_held,
        classes_attended=classes_attended,
    )
    session.add(record)
    session.flush()
    return record


def _assessment(
    session: Session,
    enrollment: Enrollment,
    *,
    status: AssessmentStatus = AssessmentStatus.GRADED,
    max_marks: float = 20,
    obtained_marks: float | None = 15,
    name: str = "Internal 1",
) -> Assessment:
    assessment = Assessment(
        enrollment_id=enrollment.id,
        type=AssessmentType.INTERNAL,
        name=name,
        max_marks=max_marks,
        obtained_marks=obtained_marks,
        status=status,
        assessment_date=date(2026, 2, 1),
    )
    session.add(assessment)
    session.flush()
    return assessment


def test_attendance_check_rejects_attended_above_held(db_session: Session) -> None:
    enrollment = _enrollment(db_session)
    with pytest.raises(IntegrityError):
        _attendance(db_session, enrollment, classes_held=4, classes_attended=5)


def test_assessment_check_rejects_graded_with_null_marks(db_session: Session) -> None:
    enrollment = _enrollment(db_session)
    with pytest.raises(IntegrityError):
        _assessment(
            db_session,
            enrollment,
            status=AssessmentStatus.GRADED,
            obtained_marks=None,
        )


def test_assessment_check_rejects_marks_above_max(db_session: Session) -> None:
    enrollment = _enrollment(db_session)
    with pytest.raises(IntegrityError):
        _assessment(db_session, enrollment, max_marks=20, obtained_marks=21)


def test_assessment_check_rejects_max_marks_zero(db_session: Session) -> None:
    enrollment = _enrollment(db_session)
    with pytest.raises(IntegrityError):
        _assessment(db_session, enrollment, max_marks=0, obtained_marks=0)


def test_duplicate_enrollment_rejected(db_session: Session) -> None:
    student = _student(db_session)
    subject = _subject(db_session)
    _enrollment(db_session, student, subject)
    with pytest.raises(IntegrityError):
        _enrollment(db_session, student, subject)


def test_duplicate_attendance_date_rejected(db_session: Session) -> None:
    enrollment = _enrollment(db_session)
    _attendance(db_session, enrollment, record_date=date(2026, 1, 12))
    with pytest.raises(IntegrityError):
        _attendance(db_session, enrollment, record_date=date(2026, 1, 12))


def test_duplicate_teaching_assignment_section_rejected(db_session: Session) -> None:
    teacher = _teacher(db_session)
    subject = _subject(db_session)
    db_session.add(
        TeachingAssignment(
            teacher_id=teacher.id, subject_id=subject.id, section="A"
        )
    )
    db_session.flush()
    db_session.add(
        TeachingAssignment(
            teacher_id=teacher.id, subject_id=subject.id, section="A"
        )
    )
    with pytest.raises(IntegrityError):
        db_session.flush()


def test_delete_enrollment_cascades_attendance_and_assessments(
    db_session: Session,
) -> None:
    enrollment = _enrollment(db_session)
    attendance = _attendance(db_session, enrollment)
    assessment = _assessment(db_session, enrollment)
    attendance_id = attendance.id
    assessment_id = assessment.id

    db_session.delete(enrollment)
    db_session.flush()

    assert db_session.get(AttendanceRecord, attendance_id) is None
    assert db_session.get(Assessment, assessment_id) is None
    assert db_session.get(Enrollment, enrollment.id) is None


def test_delete_subject_with_enrollments_fails(db_session: Session) -> None:
    subject = _subject(db_session)
    _enrollment(db_session, subject=subject)
    db_session.delete(subject)
    with pytest.raises(IntegrityError):
        db_session.flush()


def test_zero_classes_attendance_allowed(db_session: Session) -> None:
    enrollment = _enrollment(db_session)
    record = _attendance(
        db_session, enrollment, classes_held=0, classes_attended=0
    )
    assert record.id is not None


def test_create_all_builds_academic_tables(db_session: Session) -> None:
    student = _student(db_session)
    subject = _subject(db_session)
    enrollment = _enrollment(db_session, student, subject)
    habit = StudyHabit(
        student_id=student.id,
        study_hours_per_day=2.5,
        self_confidence=4,
        available_hours_per_day=4.0,
    )
    db_session.add(habit)
    db_session.flush()
    assert enrollment.id is not None
    assert habit.id is not None
