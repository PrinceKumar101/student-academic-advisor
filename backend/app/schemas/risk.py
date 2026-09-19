from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import RiskLevel


class RiskComponentOut(BaseModel):
    key: str
    label: str
    available: bool
    raw_value: float | None
    unit: str | None
    risk: float | None
    weight: float
    effective_weight: float | None
    contribution: float | None
    level: str | None
    note: str | None


class RiskOut(BaseModel):
    student_id: int
    as_of: date
    score: float | None
    level: RiskLevel
    escalated: bool
    escalation_reason: str | None
    data_completeness: float
    config_version: str
    components: list[RiskComponentOut]
    top_factors: list[str]
    flags: list[str]


class RiskHistoryItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    as_of: date
    computed_at: datetime
    score: float | None
    level: RiskLevel
    escalated: bool
    escalation_reason: str | None
    data_completeness: float
    config_version: str
    flags: list


class RiskHistoryOut(BaseModel):
    student_id: int
    items: list[RiskHistoryItemOut]


class WhatIfOverrides(BaseModel):
    model_config = ConfigDict(extra="forbid")

    attendance_percent: float | None = Field(default=None, ge=0, le=100)
    internal_percent: float | None = Field(default=None, ge=0, le=100)
    quiz_percent: float | None = Field(default=None, ge=0, le=100)
    assignment_percent: float | None = Field(default=None, ge=0, le=100)
    assignment_submission_rate: float | None = Field(default=None, ge=0, le=100)
    study_hours_per_day: float | None = Field(default=None, ge=0, le=24)
    self_confidence: int | None = Field(default=None, ge=1, le=5)

    def applied(self) -> dict[str, float | int]:
        return self.model_dump(exclude_none=True)


class WhatIfRequest(BaseModel):
    overrides: WhatIfOverrides = Field(default_factory=WhatIfOverrides)


class WhatIfScoreOut(BaseModel):
    score: float | None
    level: RiskLevel


class ChangedFactorOut(BaseModel):
    key: str
    from_value: float | None
    to_value: float | None
    risk_from: float | None
    risk_to: float | None
    contribution_delta: float | None
    hypothetical: bool


class WhatIfOut(BaseModel):
    current: WhatIfScoreOut
    simulated: WhatIfScoreOut
    difference: float | None
    changed_factors: list[ChangedFactorOut]
    persisted: bool = False
