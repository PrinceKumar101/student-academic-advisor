from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import FallbackReason, Priority, Source


class StudyPlanCreate(BaseModel):
    exam_date: date
    available_hours_per_day: float = Field(ge=0.5, le=12)
    subject_ids: list[int] = Field(default_factory=list)
    topics: dict[int, list[str]] = Field(default_factory=dict)


class StudyPlanItemPatch(BaseModel):
    is_completed: bool


class StudyPlanSubjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str


class StudyPlanItemOut(BaseModel):
    id: int
    plan_date: date
    subject: StudyPlanSubjectOut
    topic: str
    activity: str
    duration_minutes: int
    priority: Priority
    is_completed: bool
    completed_at: datetime | None = None


class StudyPlanOut(BaseModel):
    id: int
    exam_date: date
    available_hours_per_day: float
    source: Source
    prompt_version: str
    created_at: datetime
    items: list[StudyPlanItemOut]
    tips: list[str]
    fallback_reason: FallbackReason | None = None


class StudyPlanSummaryOut(BaseModel):
    id: int
    exam_date: date
    available_hours_per_day: float
    source: Source
    created_at: datetime
    item_count: int
