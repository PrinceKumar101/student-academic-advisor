from collections import defaultdict
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.engines.academic_types import (
    AssessmentRow,
    AttendanceRow,
    SemesterResultRow,
    StudentAcademicData,
    StudyHabitData,
)
from app.models.assessment import Assessment
from app.models.attendance import AttendanceRecord
from app.models.enrollment import Enrollment
from app.models.semester_result import SemesterResult
from app.models.study_habit import StudyHabit

__all__ = [
    "AssessmentRow",
    "AttendanceRow",
    "SemesterResultRow",
    "StudentAcademicData",
    "StudyHabitData",
    "load",
]


def load(
    db: Session, student_ids: list[int], as_of: date
) -> list[StudentAcademicData]:
    unique_ids = list(dict.fromkeys(student_ids))
    if not unique_ids:
        return []

    enrollments = db.execute(
        select(Enrollment).where(Enrollment.student_id.in_(unique_ids))
    ).scalars().all()
    enrollment_by_id = {row.id: row for row in enrollments}
    enrollment_ids = list(enrollment_by_id)

    attendance_rows: list[AttendanceRecord] = []
    assessment_rows: list[Assessment] = []
    if enrollment_ids:
        attendance_rows = db.execute(
            select(AttendanceRecord).where(
                AttendanceRecord.enrollment_id.in_(enrollment_ids),
                AttendanceRecord.record_date <= as_of,
            )
        ).scalars().all()
        assessment_rows = db.execute(
            select(Assessment).where(
                Assessment.enrollment_id.in_(enrollment_ids),
                Assessment.assessment_date <= as_of,
            )
        ).scalars().all()

    result_rows = db.execute(
        select(SemesterResult).where(SemesterResult.student_id.in_(unique_ids))
    ).scalars().all()
    habit_rows = db.execute(
        select(StudyHabit).where(StudyHabit.student_id.in_(unique_ids))
    ).scalars().all()

    by_student: dict[int, StudentAcademicData] = {
        student_id: StudentAcademicData(student_id=student_id)
        for student_id in unique_ids
    }
    subjects_by_student: dict[int, list[int]] = defaultdict(list)
    for enrollment in enrollments:
        subjects_by_student[enrollment.student_id].append(enrollment.subject_id)

    for student_id, subject_ids in subjects_by_student.items():
        by_student[student_id].subject_ids = subject_ids

    for row in attendance_rows:
        enrollment = enrollment_by_id[row.enrollment_id]
        by_student[enrollment.student_id].attendance.append(
            AttendanceRow(
                subject_id=enrollment.subject_id,
                record_date=row.record_date,
                classes_held=row.classes_held,
                classes_attended=row.classes_attended,
            )
        )
    for row in assessment_rows:
        enrollment = enrollment_by_id[row.enrollment_id]
        by_student[enrollment.student_id].assessments.append(
            AssessmentRow(
                subject_id=enrollment.subject_id,
                type=row.type,
                name=row.name,
                max_marks=row.max_marks,
                obtained_marks=row.obtained_marks,
                status=row.status,
                assessment_date=row.assessment_date,
            )
        )
    for row in result_rows:
        by_student[row.student_id].semester_results.append(
            SemesterResultRow(
                semester=row.semester, percentage=row.percentage, sgpa=row.sgpa
            )
        )
    for row in habit_rows:
        by_student[row.student_id].study_habit = StudyHabitData(
            study_hours_per_day=row.study_hours_per_day,
            self_confidence=row.self_confidence,
            available_hours_per_day=row.available_hours_per_day,
        )

    return [by_student[student_id] for student_id in unique_ids]
