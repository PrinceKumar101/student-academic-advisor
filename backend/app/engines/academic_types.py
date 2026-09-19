from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from app.models.enums import AssessmentStatus, AssessmentType, RiskLevel


@dataclass(frozen=True)
class AttendanceRow:
    subject_id: int
    record_date: date
    classes_held: int
    classes_attended: int


@dataclass(frozen=True)
class AssessmentRow:
    subject_id: int
    type: AssessmentType
    name: str
    max_marks: float
    obtained_marks: float | None
    status: AssessmentStatus
    assessment_date: date


@dataclass(frozen=True)
class SemesterResultRow:
    semester: int
    percentage: float
    sgpa: float | None


@dataclass(frozen=True)
class StudyHabitData:
    study_hours_per_day: float
    self_confidence: int
    available_hours_per_day: float


@dataclass(frozen=True)
class RiskSnapshotRow:
    as_of: date
    score: float | None
    level: RiskLevel


@dataclass
class StudentAcademicData:
    student_id: int
    subject_ids: list[int] = field(default_factory=list)
    attendance: list[AttendanceRow] = field(default_factory=list)
    assessments: list[AssessmentRow] = field(default_factory=list)
    semester_results: list[SemesterResultRow] = field(default_factory=list)
    study_habit: StudyHabitData | None = None
