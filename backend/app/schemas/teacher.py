from datetime import date

from pydantic import BaseModel

from app.models.enums import RiskLevel, TrendLabel
from app.schemas.students import StudentProfileOut


class TeacherStudentOut(StudentProfileOut):
    risk_score: float | None
    risk_level: RiskLevel | None
    attendance_percent: float | None
    marks_percent: float | None
    trend_label: TrendLabel | None


class SubjectMeanOut(BaseModel):
    subject_id: int
    code: str
    name: str
    mean_percent: float


class TeacherDashboardOut(BaseModel):
    as_of: date
    group_size: int
    risk_counts: dict[str, int]
    mean_attendance: float | None
    mean_marks: float | None
    subject_performance: list[SubjectMeanOut]
    trend_distribution: dict[str, int]


class SubjectAnalyticsOut(TeacherDashboardOut):
    subject_id: int
    code: str
    name: str
