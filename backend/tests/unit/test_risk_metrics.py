from datetime import date

import pytest

from app.engines.academic_types import (
    AssessmentRow,
    AttendanceRow,
    SemesterResultRow,
    StudentAcademicData,
    StudyHabitData,
)
from app.engines.metrics import to_risk_inputs
from app.engines.risk_config import RiskValidationError
from app.models.enums import AssessmentStatus, AssessmentType


def test_metrics_percent_definitions() -> None:
    data = StudentAcademicData(
        student_id=1,
        attendance=[
            AttendanceRow(1, date(2026, 9, 5), 4, 3),
            AttendanceRow(1, date(2026, 9, 12), 6, 3),
        ],
        assessments=[
            AssessmentRow(
                1,
                AssessmentType.INTERNAL,
                "I1",
                20,
                10,
                AssessmentStatus.GRADED,
                date(2026, 9, 1),
            ),
            AssessmentRow(
                1,
                AssessmentType.EXAM,
                "E1",
                80,
                40,
                AssessmentStatus.GRADED,
                date(2026, 9, 10),
            ),
            AssessmentRow(
                1,
                AssessmentType.QUIZ,
                "Q1",
                10,
                8,
                AssessmentStatus.GRADED,
                date(2026, 9, 2),
            ),
            AssessmentRow(
                1,
                AssessmentType.ASSIGNMENT,
                "A1",
                10,
                5,
                AssessmentStatus.GRADED,
                date(2026, 9, 3),
            ),
            AssessmentRow(
                1,
                AssessmentType.ASSIGNMENT,
                "A2",
                10,
                None,
                AssessmentStatus.MISSING,
                date(2026, 9, 4),
            ),
            AssessmentRow(
                1,
                AssessmentType.ASSIGNMENT,
                "A3",
                10,
                None,
                AssessmentStatus.PENDING,
                date(2026, 9, 6),
            ),
        ],
        semester_results=[
            SemesterResultRow(3, 70.0, 7.0),
            SemesterResultRow(4, 65.0, 6.5),
        ],
        study_habit=StudyHabitData(2.0, 3, 4.0),
    )
    inputs = to_risk_inputs(data)
    assert inputs.attendance_percent == 60.0
    assert inputs.internal_percent == 50.0
    assert inputs.quiz_percent == 80.0
    assert inputs.assignment_percent == 50.0
    assert inputs.assignment_submission_rate == 50.0
    assert inputs.previous_percentage == 65.0
    assert inputs.n_internal == 2
    assert inputs.n_quiz == 1
    assert inputs.n_assignment == 1
    assert inputs.newest_record_date == date(2026, 9, 12)


def test_r8_zero_classes_gives_none() -> None:
    data = StudentAcademicData(
        student_id=1,
        attendance=[AttendanceRow(1, date(2026, 9, 5), 0, 0)],
    )
    inputs = to_risk_inputs(data)
    assert inputs.attendance_percent is None


def test_r10_attended_exceeds_held() -> None:
    data = StudentAcademicData(
        student_id=1,
        attendance=[AttendanceRow(1, date(2026, 9, 5), 4, 5)],
    )
    with pytest.raises(RiskValidationError, match="exceed"):
        to_risk_inputs(data)
