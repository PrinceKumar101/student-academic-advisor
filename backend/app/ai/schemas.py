from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

Priority = Literal["HIGH", "MEDIUM", "LOW"]


class MainConcern(BaseModel):
    factor: str
    explanation: str = Field(max_length=300)


class Recommendation(BaseModel):
    action: str = Field(max_length=200)
    reason: str = Field(max_length=300)
    priority: Priority


class AnalysisAdvice(BaseModel):
    summary: str = Field(max_length=600)
    main_concerns: list[MainConcern] = Field(min_length=1, max_length=5)
    recommendations: list[Recommendation] = Field(min_length=3, max_length=6)
    priority: Priority


class PlanSlotText(BaseModel):
    slot_id: str
    topic: str = Field(max_length=80)
    activity: str = Field(max_length=200)


class PlanAdvice(BaseModel):
    slots: list[PlanSlotText]
    tips: list[str] = Field(default_factory=list, max_length=3)

    @field_validator("tips")
    @classmethod
    def tip_length(cls, value: list[str]) -> list[str]:
        if any(len(item) > 200 for item in value):
            raise ValueError("each tip must be at most 200 characters")
        return value


class InterventionSuggestion(BaseModel):
    title: str = Field(max_length=120)
    description: str = Field(max_length=400)
    priority: Priority
    reason: str = Field(max_length=300)


class InterventionSuggestionsAdvice(BaseModel):
    suggestions: list[InterventionSuggestion] = Field(min_length=1, max_length=5)


class ChatAdvice(BaseModel):
    answer: str = Field(max_length=1200)
    suggested_followups: list[str] = Field(default_factory=list, max_length=3)

    @field_validator("suggested_followups")
    @classmethod
    def followup_length(cls, value: list[str]) -> list[str]:
        if any(len(item) > 120 for item in value):
            raise ValueError("each followup must be at most 120 characters")
        return value
