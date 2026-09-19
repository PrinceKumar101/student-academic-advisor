from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import RiskLevel, TrendLabel
from app.schemas.analytics import SubjectAnalysisOut
from app.schemas.interventions import InterventionOut
from app.schemas.trends import WarningOut


class StudentProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_code: str
    full_name: str
    department: str
    semester: int
    section: str


class StudyHabitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    student_id: int
    study_hours_per_day: float
    self_confidence: int
    available_hours_per_day: float


class StudyHabitUpdate(BaseModel):
    study_hours_per_day: float = Field(ge=0, le=24)
    self_confidence: int = Field(ge=1, le=5)
    available_hours_per_day: float = Field(ge=0, le=24)


class SemesterResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    semester: int
    percentage: float
    sgpa: float | None


class SemesterResultUpdate(BaseModel):
    percentage: float = Field(ge=0, le=100)
    sgpa: float | None = Field(default=None, ge=0, le=10)


class OverviewRiskOut(BaseModel):
    score: float | None
    level: RiskLevel
    escalated: bool
    escalation_reason: str | None
    data_completeness: float
    config_version: str
    flags: list[str]


class OverviewTrendSummaryOut(BaseModel):
    overall_label: TrendLabel
    overall_slope: float | None
    attendance_label: TrendLabel
    attendance_slope: float | None


class StudentOverviewOut(BaseModel):
    student_id: int
    as_of: date
    profile: StudentProfileOut
    risk: OverviewRiskOut
    top_factors: list[str]
    subjects: list[SubjectAnalysisOut]
    trend_summary: OverviewTrendSummaryOut
    warnings: list[WarningOut]
    open_interventions: list[InterventionOut]
