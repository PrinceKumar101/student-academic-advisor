from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from app.engines.academic_types import StudentAcademicData
from app.engines.risk_config import RiskValidationError
from app.models.enums import AssessmentStatus, AssessmentType


@dataclass(frozen=True)
class RiskInputs:
    attendance_percent: float | None = None
    internal_percent: float | None = None
    quiz_percent: float | None = None
    assignment_percent: float | None = None
    assignment_submission_rate: float | None = None
    previous_percentage: float | None = None
    study_hours_per_day: float | None = None
    self_confidence: int | None = None
    n_internal: int = 0
    n_quiz: int = 0
    n_assignment: int = 0
    newest_record_date: date | None = None


def _ratio_percent(obtained: float, maximum: float) -> float | None:
    if maximum <= 0:
        return None
    return obtained / maximum * 100.0


def _graded_percent(
    rows: list,
) -> tuple[float | None, int]:
    graded = [
        row
        for row in rows
        if row.status is AssessmentStatus.GRADED and row.obtained_marks is not None
    ]
    total_max = sum(row.max_marks for row in graded)
    total_obtained = sum(row.obtained_marks for row in graded)
    return _ratio_percent(total_obtained, total_max), len(graded)


def to_risk_inputs(data: StudentAcademicData) -> RiskInputs:
    for row in data.attendance:
        if row.classes_attended > row.classes_held:
            raise RiskValidationError("classes_attended cannot exceed classes_held")
        if row.classes_held < 0 or row.classes_attended < 0:
            raise RiskValidationError("class counts cannot be negative")

    held = sum(row.classes_held for row in data.attendance)
    attended = sum(row.classes_attended for row in data.attendance)
    attendance_percent = (attended / held * 100.0) if held > 0 else None

    internals = [
        row
        for row in data.assessments
        if row.type in (AssessmentType.INTERNAL, AssessmentType.EXAM)
    ]
    quizzes = [row for row in data.assessments if row.type is AssessmentType.QUIZ]
    assignments = [
        row for row in data.assessments if row.type is AssessmentType.ASSIGNMENT
    ]

    internal_percent, n_internal = _graded_percent(internals)
    quiz_percent, n_quiz = _graded_percent(quizzes)
    assignment_percent, n_assignment = _graded_percent(assignments)

    graded_or_missing = [
        row
        for row in assignments
        if row.status in (AssessmentStatus.GRADED, AssessmentStatus.MISSING)
    ]
    if graded_or_missing:
        graded_count = sum(
            1 for row in graded_or_missing if row.status is AssessmentStatus.GRADED
        )
        assignment_submission_rate = graded_count / len(graded_or_missing) * 100.0
    else:
        assignment_submission_rate = None

    previous_percentage = None
    if data.semester_results:
        latest = max(data.semester_results, key=lambda row: row.semester)
        previous_percentage = latest.percentage

    study_hours = None
    confidence = None
    if data.study_habit is not None:
        study_hours = data.study_habit.study_hours_per_day
        confidence = data.study_habit.self_confidence

    dated = [row.record_date for row in data.attendance]
    dated.extend(row.assessment_date for row in data.assessments)
    newest = max(dated) if dated else None

    inputs = RiskInputs(
        attendance_percent=attendance_percent,
        internal_percent=internal_percent,
        quiz_percent=quiz_percent,
        assignment_percent=assignment_percent,
        assignment_submission_rate=assignment_submission_rate,
        previous_percentage=previous_percentage,
        study_hours_per_day=study_hours,
        self_confidence=confidence,
        n_internal=n_internal,
        n_quiz=n_quiz,
        n_assignment=n_assignment,
        newest_record_date=newest,
    )
    validate_risk_inputs(inputs)
    return inputs


def validate_risk_inputs(inputs: RiskInputs) -> None:
    percents = {
        "attendance_percent": inputs.attendance_percent,
        "internal_percent": inputs.internal_percent,
        "quiz_percent": inputs.quiz_percent,
        "assignment_percent": inputs.assignment_percent,
        "assignment_submission_rate": inputs.assignment_submission_rate,
        "previous_percentage": inputs.previous_percentage,
    }
    for name, value in percents.items():
        if value is None:
            continue
        if value < 0 or value > 100:
            raise RiskValidationError(f"{name} must be between 0 and 100")
    if inputs.study_hours_per_day is not None and inputs.study_hours_per_day < 0:
        raise RiskValidationError("study_hours_per_day cannot be negative")
    if inputs.self_confidence is not None and not 1 <= inputs.self_confidence <= 5:
        raise RiskValidationError("self_confidence must be between 1 and 5")
    for name, value in (
        ("n_internal", inputs.n_internal),
        ("n_quiz", inputs.n_quiz),
        ("n_assignment", inputs.n_assignment),
    ):
        if value < 0:
            raise RiskValidationError(f"{name} cannot be negative")
