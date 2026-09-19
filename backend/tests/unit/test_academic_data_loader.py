from datetime import date

from sqlalchemy import event, func, select
from sqlalchemy.orm import Session
from tests.helpers import (
    add_assessment,
    add_attendance,
    add_semester_result,
    add_student,
    add_study_habit,
    add_subject,
    enroll,
)

from app.models.attendance import AttendanceRecord
from app.models.enums import AssessmentStatus, AssessmentType
from app.services.academic_data_loader import load


def test_loader_matches_sql_and_respects_as_of(
    db_session: Session, demo_password_hash: str
) -> None:
    _u, student = add_student(
        db_session,
        password_hash=demo_password_hash,
        email="a@demo.edu",
        student_code="A001",
    )
    subject = add_subject(db_session, code="CS301", name="DSA")
    enrollment = enroll(db_session, student, subject)
    add_attendance(
        db_session,
        enrollment,
        record_date=date(2026, 9, 1),
        classes_held=4,
        classes_attended=3,
    )
    add_attendance(
        db_session,
        enrollment,
        record_date=date(2026, 9, 19),
        classes_held=2,
        classes_attended=2,
    )
    add_assessment(
        db_session,
        enrollment,
        assessment_date=date(2026, 9, 1),
        name="Early",
        assessment_type=AssessmentType.QUIZ,
        max_marks=10,
        obtained_marks=7,
    )
    add_assessment(
        db_session,
        enrollment,
        assessment_date=date(2026, 9, 19),
        name="Late",
        assessment_type=AssessmentType.INTERNAL,
        max_marks=20,
        obtained_marks=18,
        status=AssessmentStatus.GRADED,
    )
    add_semester_result(db_session, student, semester=4, percentage=80.0)
    add_study_habit(db_session, student, study_hours_per_day=2.0)

    cutoff = date(2026, 9, 10)
    [data] = load(db_session, [student.id], cutoff)
    assert data.subject_ids == [subject.id]
    assert len(data.attendance) == 1
    assert data.attendance[0].classes_held == 4
    assert len(data.assessments) == 1
    assert data.assessments[0].name == "Early"
    assert data.semester_results[0].percentage == 80.0
    assert data.study_habit is not None
    assert data.study_habit.study_hours_per_day == 2.0

    held, attended = db_session.execute(
        select(
            func.coalesce(func.sum(AttendanceRecord.classes_held), 0),
            func.coalesce(func.sum(AttendanceRecord.classes_attended), 0),
        ).where(
            AttendanceRecord.enrollment_id == enrollment.id,
            AttendanceRecord.record_date <= cutoff,
        )
    ).one()
    assert sum(row.classes_held for row in data.attendance) == held
    assert sum(row.classes_attended for row in data.attendance) == attended

    later = load(db_session, [student.id], date(2026, 9, 19))[0]
    assert len(later.attendance) == 2
    assert len(later.assessments) == 2


def test_loader_query_count_does_not_grow_with_students(
    db_session: Session, demo_password_hash: str
) -> None:
    subject = add_subject(db_session, code="CS301", name="DSA")
    ids: list[int] = []
    for index in range(8):
        _user, student = add_student(
            db_session,
            password_hash=demo_password_hash,
            email=f"s{index}@demo.edu",
            student_code=f"S{index:03d}",
        )
        enrollment = enroll(db_session, student, subject)
        add_attendance(
            db_session,
            enrollment,
            record_date=date(2026, 9, 1),
            classes_held=2,
            classes_attended=2,
        )
        ids.append(student.id)

    counts: list[int] = []

    def _count(_conn, _cursor, _statement, _parameters, _context, _executemany) -> None:
        counts.append(1)

    engine = db_session.get_bind()
    event.listen(engine, "after_cursor_execute", _count)
    try:
        load(db_session, ids[:1], date(2026, 9, 19))
        first = len(counts)
        counts.clear()
        load(db_session, ids, date(2026, 9, 19))
        second = len(counts)
    finally:
        event.remove(engine, "after_cursor_execute", _count)

    assert first == second
    assert first <= 6


def test_loader_empty_ids(db_session: Session) -> None:
    assert load(db_session, [], date(2026, 9, 19)) == []
