from datetime import date, timedelta

from app.engines.academic_types import (
    AssessmentRow,
    AttendanceRow,
    RiskSnapshotRow,
    StudentAcademicData,
)
from app.engines.warnings import detect_warnings
from app.models.enums import (
    AssessmentStatus,
    AssessmentType,
    RiskLevel,
    WarningSeverity,
)


def _data(
    *,
    attendance: list[AttendanceRow] | None = None,
    assessments: list[AssessmentRow] | None = None,
) -> StudentAcademicData:
    return StudentAcademicData(
        student_id=1,
        subject_ids=[1],
        attendance=attendance or [],
        assessments=assessments or [],
    )


def test_attendance_drop_warning_srs_example() -> None:
    attendance: list[AttendanceRow] = []
    start = date(2026, 6, 1)
    for week in range(8):
        attendance.append(
            AttendanceRow(1, start + timedelta(weeks=week), 10, 8)
        )
    for week in range(8, 12):
        attendance.append(
            AttendanceRow(1, start + timedelta(weeks=week), 10, 7)
        )
    # previous 8 weeks 80%; last 4 weeks 70% = 10 pp → WARNING
    warnings = detect_warnings(_data(attendance=attendance), [])
    drop = next(item for item in warnings if item.code == "ATTENDANCE_DROP")
    assert drop.severity is WarningSeverity.WARNING
    assert drop.previous_value == 80.0
    assert drop.current_value == 70.0


def test_attendance_drop_srs_82_to_67() -> None:
    attendance: list[AttendanceRow] = []
    start = date(2026, 6, 1)
    for week in range(8):
        attendance.append(
            AttendanceRow(1, start + timedelta(weeks=week), 100, 82)
        )
    for week in range(8, 12):
        attendance.append(
            AttendanceRow(1, start + timedelta(weeks=week), 100, 67)
        )
    warnings = detect_warnings(_data(attendance=attendance), [])
    drop = next(item for item in warnings if item.code == "ATTENDANCE_DROP")
    assert drop.severity is WarningSeverity.WARNING
    assert drop.previous_value == 82.0
    assert drop.current_value == 67.0


def test_quiz_drop_critical_srs_example() -> None:
    assessments = [
        AssessmentRow(
            1,
            AssessmentType.QUIZ,
            "Q1",
            100,
            76,
            AssessmentStatus.GRADED,
            date(2026, 6, 1),
        ),
        AssessmentRow(
            1,
            AssessmentType.QUIZ,
            "Q2",
            100,
            48,
            AssessmentStatus.GRADED,
            date(2026, 6, 8),
        ),
    ]
    warnings = detect_warnings(_data(assessments=assessments), [])
    quiz = next(item for item in warnings if item.code == "QUIZ_DROP")
    assert quiz.severity is WarningSeverity.CRITICAL
    assert quiz.previous_value == 76.0
    assert quiz.current_value == 48.0


def test_missing_assignments_and_risk_increase() -> None:
    assessments = [
        AssessmentRow(
            1,
            AssessmentType.ASSIGNMENT,
            "A1",
            10,
            None,
            AssessmentStatus.MISSING,
            date(2026, 6, 1),
        ),
        AssessmentRow(
            1,
            AssessmentType.ASSIGNMENT,
            "A2",
            10,
            None,
            AssessmentStatus.MISSING,
            date(2026, 6, 8),
        ),
        AssessmentRow(
            1,
            AssessmentType.ASSIGNMENT,
            "A3",
            10,
            None,
            AssessmentStatus.MISSING,
            date(2026, 6, 15),
        ),
    ]
    snapshots = [
        RiskSnapshotRow(date(2026, 7, 1), 20.0, RiskLevel.LOW),
        RiskSnapshotRow(date(2026, 8, 1), 80.0, RiskLevel.HIGH),
    ]
    warnings = {
        item.code: item
        for item in detect_warnings(_data(assessments=assessments), snapshots)
    }
    assert warnings["MISSING_ASSIGNMENTS"].severity is WarningSeverity.CRITICAL
    assert warnings["RISK_LEVEL_INCREASE"].severity is WarningSeverity.CRITICAL


def test_empty_data_has_no_warnings() -> None:
    assert detect_warnings(_data(), []) == []
