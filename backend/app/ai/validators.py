from __future__ import annotations

import json
import re
from dataclasses import dataclass

from pydantic import ValidationError

from app.ai.context_builder import StudentAcademicContext
from app.ai.schemas import (
    AnalysisAdvice,
    ChatAdvice,
    InterventionSuggestionsAdvice,
    PlanAdvice,
)

REASON_INVALID = "INVALID_OUTPUT"
REASON_UNGROUNDED = "UNGROUNDED_OUTPUT"

_PERCENT = re.compile(r"(\d+(?:\.\d+)?)\s*%")
_RISK_SCORE = re.compile(r"risk score of (\d+(?:\.\d+)?)", re.I)


@dataclass(frozen=True)
class ValidationOutcome:
    advice: AnalysisAdvice | None
    reason: str | None

    @property
    def ok(self) -> bool:
        return self.advice is not None and self.reason is None


@dataclass(frozen=True)
class PlanValidationOutcome:
    advice: PlanAdvice | None
    reason: str | None

    @property
    def ok(self) -> bool:
        return self.advice is not None and self.reason is None


def extract_grounded_claims(text: str) -> list[float]:
    values = [float(match) for match in _PERCENT.findall(text)]
    values.extend(float(match) for match in _RISK_SCORE.findall(text))
    return values


def is_grounded(text: str, context: StudentAcademicContext) -> bool:
    allowed = context.grounding_numbers()
    for claim in extract_grounded_claims(text):
        if not any(abs(claim - value) <= 0.5 for value in allowed):
            return False
    return True


def _advice_text(advice: AnalysisAdvice) -> str:
    parts = [advice.summary]
    for concern in advice.main_concerns:
        parts.append(concern.explanation)
    for item in advice.recommendations:
        parts.append(item.action)
        parts.append(item.reason)
    return " ".join(parts)


def validate_analysis_output(
    raw: str, context: StudentAcademicContext
) -> ValidationOutcome:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return ValidationOutcome(None, REASON_INVALID)
    if not isinstance(payload, dict):
        return ValidationOutcome(None, REASON_INVALID)
    try:
        advice = AnalysisAdvice.model_validate(payload)
    except ValidationError:
        return ValidationOutcome(None, REASON_INVALID)

    allowed = set(context.factor_keys)
    if any(concern.factor not in allowed for concern in advice.main_concerns):
        return ValidationOutcome(None, REASON_INVALID)
    if not is_grounded(_advice_text(advice), context):
        return ValidationOutcome(None, REASON_UNGROUNDED)
    return ValidationOutcome(advice, None)


def _plan_text(advice: PlanAdvice) -> str:
    parts = [item.topic + " " + item.activity for item in advice.slots]
    parts.extend(advice.tips)
    return " ".join(parts)


def validate_plan_output(
    raw: str,
    expected_slot_ids: list[str],
    allowed_topics: dict[str, list[str]],
    subject_codes: dict[str, str],
) -> PlanValidationOutcome:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return PlanValidationOutcome(None, REASON_INVALID)
    if not isinstance(payload, dict):
        return PlanValidationOutcome(None, REASON_INVALID)
    try:
        advice = PlanAdvice.model_validate(payload)
    except ValidationError:
        return PlanValidationOutcome(None, REASON_INVALID)

    returned = [item.slot_id for item in advice.slots]
    expected = list(expected_slot_ids)
    if sorted(returned) != sorted(expected) or len(returned) != len(set(returned)):
        return PlanValidationOutcome(None, REASON_INVALID)
    if any(len(tip) > 200 for tip in advice.tips):
        return PlanValidationOutcome(None, REASON_INVALID)

    for item in advice.slots:
        code = subject_codes[item.slot_id]
        allowed = allowed_topics.get(code) or []
        if allowed and item.topic not in allowed:
            return PlanValidationOutcome(None, REASON_INVALID)

    if extract_grounded_claims(_plan_text(advice)):
        return PlanValidationOutcome(None, REASON_UNGROUNDED)
    return PlanValidationOutcome(advice, None)


@dataclass(frozen=True)
class ChatValidationOutcome:
    advice: ChatAdvice | None
    reason: str | None

    @property
    def ok(self) -> bool:
        return self.advice is not None and self.reason is None


def _chat_text(advice: ChatAdvice) -> str:
    return " ".join([advice.answer, *advice.suggested_followups])


@dataclass(frozen=True)
class SuggestionsValidationOutcome:
    advice: InterventionSuggestionsAdvice | None
    reason: str | None

    @property
    def ok(self) -> bool:
        return self.advice is not None and self.reason is None


def _suggestions_text(advice: InterventionSuggestionsAdvice) -> str:
    parts: list[str] = []
    for item in advice.suggestions:
        parts.extend([item.title, item.description, item.reason])
    return " ".join(parts)


def validate_suggestions_output(
    raw: str, context: StudentAcademicContext
) -> SuggestionsValidationOutcome:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return SuggestionsValidationOutcome(None, REASON_INVALID)
    if not isinstance(payload, dict):
        return SuggestionsValidationOutcome(None, REASON_INVALID)
    try:
        advice = InterventionSuggestionsAdvice.model_validate(payload)
    except ValidationError:
        return SuggestionsValidationOutcome(None, REASON_INVALID)
    if not is_grounded(_suggestions_text(advice), context):
        return SuggestionsValidationOutcome(None, REASON_UNGROUNDED)
    return SuggestionsValidationOutcome(advice, None)


def validate_chat_output(
    raw: str, context: StudentAcademicContext
) -> ChatValidationOutcome:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return ChatValidationOutcome(None, REASON_INVALID)
    if not isinstance(payload, dict):
        return ChatValidationOutcome(None, REASON_INVALID)
    try:
        advice = ChatAdvice.model_validate(payload)
    except ValidationError:
        return ChatValidationOutcome(None, REASON_INVALID)
    if not is_grounded(_chat_text(advice), context):
        return ChatValidationOutcome(None, REASON_UNGROUNDED)
    return ChatValidationOutcome(advice, None)
