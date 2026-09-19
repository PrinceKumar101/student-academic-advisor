from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.models.enums import ChatMessageRole, FallbackReason, Source


class AnalysisRequest(BaseModel):
    student_id: str = "me"
    refresh: bool = False


class InterventionSuggestionsRequest(BaseModel):
    student_id: str


class AnalysisConcernOut(BaseModel):
    factor: str
    explanation: str


class AnalysisRecommendationOut(BaseModel):
    action: str
    reason: str
    priority: str


class AnalysisAdviceOut(BaseModel):
    summary: str
    main_concerns: list[AnalysisConcernOut]
    recommendations: list[AnalysisRecommendationOut]
    priority: str


class AnalysisOut(BaseModel):
    source: Source
    generated_at: datetime
    cached: bool
    facts: dict
    advice: AnalysisAdviceOut
    fallback_reason: FallbackReason | None = None


class UsageBucketOut(BaseModel):
    used: int
    limit: int
    remaining: int = Field(ge=0)


class UsageOut(BaseModel):
    analysis: UsageBucketOut
    chat: UsageBucketOut
    plans: UsageBucketOut


class InterventionSuggestionOut(BaseModel):
    title: str
    description: str
    priority: str
    reason: str


class InterventionSuggestionsOut(BaseModel):
    source: Source
    generated_at: datetime
    student_id: int
    prompt_version: str
    suggestions: list[InterventionSuggestionOut]
    fallback_reason: FallbackReason | None = None


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)

    @field_validator("question")
    @classmethod
    def strip_question(cls, value: str) -> str:
        text = value.strip()
        if not text:
            raise ValueError("question must not be empty")
        if len(text) > 500:
            raise ValueError("question must be at most 500 characters")
        return text


class ChatOut(BaseModel):
    source: Source
    generated_at: datetime
    answer: str
    suggested_followups: list[str]
    fallback_reason: FallbackReason | None = None


class ChatMessageOut(BaseModel):
    id: int
    role: ChatMessageRole
    content: str
    source: Source | None = None
    created_at: datetime


class ChatHistoryOut(BaseModel):
    messages: list[ChatMessageOut]
