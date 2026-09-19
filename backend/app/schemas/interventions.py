from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.enums import (
    InterventionStatus,
    Priority,
    ProgressDirection,
    RiskLevel,
)


class InterventionCreate(BaseModel):
    student_id: int
    subject_id: int | None = None
    title: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    priority: Priority = Priority.MEDIUM
    due_date: date | None = None


class InterventionPatch(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    priority: Priority | None = None
    due_date: date | None = None
    subject_id: int | None = None
    status: InterventionStatus | None = None
    completion_note: str | None = Field(default=None, max_length=2000)


class InterventionOut(BaseModel):
    id: int
    student_id: int
    teacher_id: int
    subject_id: int | None
    title: str
    description: str | None
    priority: Priority
    status: InterventionStatus
    due_date: date | None
    baseline_score: float | None
    baseline_level: RiskLevel
    baseline_at: datetime
    outcome_score: float | None
    outcome_level: RiskLevel | None
    outcome_at: datetime | None
    completion_note: str | None
    created_at: datetime
    updated_at: datetime


class RiskSnapshotOut(BaseModel):
    score: float | None
    level: RiskLevel
    at: datetime | None = None
    as_of: date | None = None


class InterventionProgressOut(BaseModel):
    baseline: RiskSnapshotOut
    current: RiskSnapshotOut
    change: float | None
    direction: ProgressDirection
    days_elapsed: int
    note: str
