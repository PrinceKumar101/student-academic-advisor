from datetime import date

from pydantic import BaseModel

from app.models.enums import SubjectBand


class SubjectAnalysisOut(BaseModel):
    subject_id: int
    code: str
    name: str
    performance_percent: float | None
    band: SubjectBand | None
    attendance_percent: float | None
    attendance_alert: bool


class SubjectAnalysisListOut(BaseModel):
    student_id: int
    as_of: date
    subjects: list[SubjectAnalysisOut]


class ComparisonMetricsOut(BaseModel):
    attendance_percent: float | None
    marks_percent: float | None


class ComparisonGroupOut(BaseModel):
    department: str
    semester: int
    section: str


class ComparisonOut(BaseModel):
    student_id: int
    as_of: date
    available: bool
    group_size: int
    group: ComparisonGroupOut
    student: ComparisonMetricsOut | None
    class_average: ComparisonMetricsOut | None
    reason: str | None
