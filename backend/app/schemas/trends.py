from datetime import date

from pydantic import BaseModel

from app.models.enums import AssessmentType, SuddenChange, TrendLabel, WarningSeverity


class TrendPointOut(BaseModel):
    on: date
    value: float


class TrendSeriesOut(BaseModel):
    label: TrendLabel
    slope: float | None
    point_count: int
    first: float | None
    last: float | None
    mean: float | None
    sudden_change: SuddenChange | None
    points: list[TrendPointOut]


class TypedTrendOut(TrendSeriesOut):
    type: AssessmentType


class SubjectTrendOut(TrendSeriesOut):
    subject_id: int
    subject_code: str
    subject_name: str


class TrendsOut(BaseModel):
    student_id: int
    as_of: date
    overall: TrendSeriesOut
    by_type: list[TypedTrendOut]
    by_subject: list[SubjectTrendOut]
    attendance: TrendSeriesOut
    risk: TrendSeriesOut


class WarningOut(BaseModel):
    code: str
    severity: WarningSeverity
    message: str
    metric: str
    previous_value: float | None
    current_value: float | None


class WarningsOut(BaseModel):
    student_id: int
    as_of: date
    warnings: list[WarningOut]
