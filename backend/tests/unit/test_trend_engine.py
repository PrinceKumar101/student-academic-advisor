from datetime import date

from app.engines.academic_types import AssessmentRow, AttendanceRow, StudentAcademicData
from app.engines.trend_engine import (
    SeriesPoint,
    analyze_series,
    assessment_points,
    build_student_trends,
    weekly_attendance_points,
)
from app.models.enums import AssessmentStatus, AssessmentType, SuddenChange, TrendLabel


def test_slope_declining_example() -> None:
    result = analyze_series(
        [
            SeriesPoint(date(2026, 6, 1), 72),
            SeriesPoint(date(2026, 6, 8), 69),
            SeriesPoint(date(2026, 6, 15), 63),
            SeriesPoint(date(2026, 6, 22), 55),
        ]
    )
    assert result.slope == -5.7
    assert result.label is TrendLabel.DECLINING
    assert result.mean == 64.8
    assert result.sudden_change is None


def test_flat_series_is_stable() -> None:
    result = analyze_series(
        [
            SeriesPoint(date(2026, 6, 1), 70),
            SeriesPoint(date(2026, 6, 8), 70),
            SeriesPoint(date(2026, 6, 15), 70),
        ]
    )
    assert result.slope == 0.0
    assert result.label is TrendLabel.STABLE


def test_two_points_insufficient() -> None:
    result = analyze_series(
        [SeriesPoint(date(2026, 6, 1), 70), SeriesPoint(date(2026, 6, 8), 40)]
    )
    assert result.label is TrendLabel.INSUFFICIENT_DATA
    assert result.slope is None
    assert result.point_count == 2


def test_empty_series_insufficient() -> None:
    result = analyze_series([])
    assert result.label is TrendLabel.INSUFFICIENT_DATA
    assert result.point_count == 0
    assert result.first is None


def test_sudden_rise() -> None:
    result = analyze_series(
        [
            SeriesPoint(date(2026, 6, 1), 50),
            SeriesPoint(date(2026, 6, 8), 52),
            SeriesPoint(date(2026, 6, 15), 51),
            SeriesPoint(date(2026, 6, 22), 90),
        ]
    )
    assert result.sudden_change is SuddenChange.SUDDEN_RISE


def test_improving_slope() -> None:
    result = analyze_series(
        [
            SeriesPoint(date(2026, 6, 1), 40),
            SeriesPoint(date(2026, 6, 8), 50),
            SeriesPoint(date(2026, 6, 15), 60),
            SeriesPoint(date(2026, 6, 22), 70),
        ]
    )
    assert result.slope == 10.0
    assert result.label is TrendLabel.IMPROVING


def test_assessment_and_attendance_series_builders() -> None:
    data = StudentAcademicData(
        student_id=1,
        subject_ids=[1, 2],
        attendance=[
            AttendanceRow(1, date(2026, 6, 1), 10, 8),
            AttendanceRow(2, date(2026, 6, 1), 10, 6),
            AttendanceRow(1, date(2026, 6, 8), 10, 5),
        ],
        assessments=[
            AssessmentRow(
                1,
                AssessmentType.QUIZ,
                "Q1",
                10,
                8,
                AssessmentStatus.GRADED,
                date(2026, 6, 2),
            ),
            AssessmentRow(
                1,
                AssessmentType.QUIZ,
                "Q2",
                10,
                None,
                AssessmentStatus.PENDING,
                date(2026, 6, 9),
            ),
            AssessmentRow(
                2,
                AssessmentType.INTERNAL,
                "I1",
                20,
                10,
                AssessmentStatus.GRADED,
                date(2026, 6, 3),
            ),
        ],
    )
    overall = assessment_points(data.assessments)
    assert [point.value for point in overall] == [80.0, 50.0]
    weekly = weekly_attendance_points(data.attendance)
    assert weekly[0].value == 70.0
    assert weekly[1].value == 50.0
    trends = build_student_trends(data, [])
    assert trends.overall.point_count == 2
    assert trends.by_type[AssessmentType.QUIZ].point_count == 1
    assert trends.by_subject[1].point_count == 1
    assert trends.attendance.point_count == 2
    assert trends.risk.label is TrendLabel.INSUFFICIENT_DATA
