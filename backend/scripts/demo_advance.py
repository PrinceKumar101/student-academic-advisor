"""Add post-intervention recovery records for the demo student."""

from __future__ import annotations

import argparse
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models.assessment import Assessment
from app.models.attendance import AttendanceRecord
from app.models.enrollment import Enrollment
from app.models.enums import AssessmentStatus, AssessmentType
from app.models.student import Student
from app.models.user import User
from scripts.seed_generator import DEFAULT_AS_OF, RAHUL_EMAIL

ADVANCE_WEEKS = 4


def advance_as_of(as_of: date = DEFAULT_AS_OF, weeks: int = ADVANCE_WEEKS) -> date:
    return as_of + timedelta(weeks=weeks)


def _student_by_email(session: Session, email: str) -> Student:
    student = session.execute(
        select(Student)
        .join(User, Student.user_id == User.id)
        .where(User.email == email)
    ).scalar_one_or_none()
    if student is None:
        raise SystemExit(f"Student not found for {email}")
    return student


def advance_student(
    session: Session,
    student: Student,
    *,
    as_of: date = DEFAULT_AS_OF,
    weeks: int = ADVANCE_WEEKS,
) -> date:
    enrollments = session.execute(
        select(Enrollment)
        .options(selectinload(Enrollment.attendance_records))
        .where(Enrollment.student_id == student.id)
    ).scalars().all()
    if not enrollments:
        raise SystemExit("Student has no enrollments to advance")

    last_dates = [
        max((row.record_date for row in enrollment.attendance_records), default=as_of)
        for enrollment in enrollments
    ]
    start = max(last_dates + [as_of]) + timedelta(days=7)

    for week in range(weeks):
        record_date = start + timedelta(weeks=week)
        for enrollment in enrollments:
            session.add(
                AttendanceRecord(
                    enrollment_id=enrollment.id,
                    record_date=record_date,
                    classes_held=5,
                    classes_attended=5,
                )
            )
            if week == weeks - 1:
                session.add(
                    Assessment(
                        enrollment_id=enrollment.id,
                        type=AssessmentType.INTERNAL,
                        name="Recovery internal",
                        max_marks=30.0,
                        obtained_marks=24.0,
                        status=AssessmentStatus.GRADED,
                        assessment_date=record_date,
                    )
                )
                session.add(
                    Assessment(
                        enrollment_id=enrollment.id,
                        type=AssessmentType.ASSIGNMENT,
                        name="Recovery assignment",
                        max_marks=10.0,
                        obtained_marks=8.0,
                        status=AssessmentStatus.GRADED,
                        assessment_date=record_date,
                    )
                )
    session.flush()
    return start + timedelta(weeks=weeks - 1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Add recovery records after the demo as_of."
    )
    parser.add_argument("--email", default=RAHUL_EMAIL)
    parser.add_argument("--as-of", default=DEFAULT_AS_OF.isoformat())
    parser.add_argument("--weeks", type=int, default=ADVANCE_WEEKS)
    args = parser.parse_args()
    settings = get_settings()
    print(f"Advancing {args.email} in {settings.database_url}")
    session = SessionLocal()
    try:
        student = _student_by_email(session, args.email)
        new_as_of = advance_student(
            session,
            student,
            as_of=date.fromisoformat(args.as_of),
            weeks=args.weeks,
        )
        session.commit()
        print(f"Added {args.weeks} recovery weeks. New as_of: {new_as_of.isoformat()}")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
