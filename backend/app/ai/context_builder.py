from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass

from app.engines.risk_config import round1


@dataclass(frozen=True)
class SubjectFact:
    code: str
    name: str
    attendance_percent: float | None
    performance_percent: float | None
    band: str | None


@dataclass(frozen=True)
class FactorFact:
    key: str
    raw_value: float | None
    unit: str | None
    risk: float | None


@dataclass(frozen=True)
class TrendFact:
    series: str
    label: str
    first: float | None
    last: float | None


@dataclass(frozen=True)
class WarningFact:
    code: str
    severity: str
    message: str
    metric: str
    previous_value: float | None
    current_value: float | None


@dataclass(frozen=True)
class StudentAcademicContext:
    overall_attendance_percent: float | None
    subjects: tuple[SubjectFact, ...]
    risk_score: float | None
    risk_level: str
    data_completeness: float
    top_factors: tuple[FactorFact, ...]
    weak_subjects: tuple[SubjectFact, ...]
    trends: tuple[TrendFact, ...]
    warnings: tuple[WarningFact, ...]
    study_hours_per_day: float | None
    self_confidence: int | None
    factor_keys: tuple[str, ...]

    def to_facts_dict(self) -> dict:
        return {
            "overall_attendance_percent": self.overall_attendance_percent,
            "subjects": [
                {
                    "code": item.code,
                    "name": item.name,
                    "attendance_percent": item.attendance_percent,
                    "performance_percent": item.performance_percent,
                    "band": item.band,
                }
                for item in self.subjects
            ],
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "data_completeness": self.data_completeness,
            "top_factors": [
                {
                    "key": item.key,
                    "raw_value": item.raw_value,
                    "unit": item.unit,
                    "risk": item.risk,
                }
                for item in self.top_factors
            ],
            "weak_subjects": [
                {
                    "code": item.code,
                    "name": item.name,
                    "attendance_percent": item.attendance_percent,
                    "performance_percent": item.performance_percent,
                    "band": item.band,
                }
                for item in self.weak_subjects
            ],
            "trends": [
                {
                    "series": item.series,
                    "label": item.label,
                    "first": item.first,
                    "last": item.last,
                }
                for item in self.trends
            ],
            "warnings": [
                {
                    "code": item.code,
                    "severity": item.severity,
                    "message": item.message,
                    "metric": item.metric,
                    "previous_value": item.previous_value,
                    "current_value": item.current_value,
                }
                for item in self.warnings
            ],
            "study_hours_per_day": self.study_hours_per_day,
            "self_confidence": self.self_confidence,
        }

    def to_prompt_json(self) -> str:
        return json.dumps(self.to_facts_dict(), sort_keys=True)

    def grounding_numbers(self) -> list[float]:
        values: list[float] = []
        if self.overall_attendance_percent is not None:
            values.append(self.overall_attendance_percent)
        if self.risk_score is not None:
            values.append(self.risk_score)
        values.append(self.data_completeness)
        for subject in self.subjects:
            if subject.attendance_percent is not None:
                values.append(subject.attendance_percent)
            if subject.performance_percent is not None:
                values.append(subject.performance_percent)
        for factor in self.top_factors:
            if factor.raw_value is not None:
                values.append(factor.raw_value)
            if factor.risk is not None:
                values.append(factor.risk)
        for trend in self.trends:
            if trend.first is not None:
                values.append(trend.first)
            if trend.last is not None:
                values.append(trend.last)
        for warning in self.warnings:
            if warning.previous_value is not None:
                values.append(warning.previous_value)
            if warning.current_value is not None:
                values.append(warning.current_value)
        if self.study_hours_per_day is not None:
            values.append(self.study_hours_per_day)
        return values

    def input_hash(self) -> str:
        payload = json.dumps(
            self.to_facts_dict(), sort_keys=True, separators=(",", ":")
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class SubjectMeta:
    code: str
    name: str


def _round_or_none(value: float | None) -> float | None:
    return round1(value) if value is not None else None


def build_context(
    *,
    overall_attendance_percent: float | None,
    subject_rows: list[tuple[SubjectMeta, float | None, float | None, str | None]],
    risk_score: float | None,
    risk_level: str,
    data_completeness: float,
    top_factors: list[FactorFact],
    trends: list[TrendFact],
    warnings: list[WarningFact],
    study_hours_per_day: float | None,
    self_confidence: int | None,
    extra_factor_keys: list[str] | None = None,
) -> StudentAcademicContext:
    subjects = tuple(
        SubjectFact(
            code=meta.code,
            name=meta.name,
            attendance_percent=_round_or_none(attendance),
            performance_percent=_round_or_none(performance),
            band=band,
        )
        for meta, attendance, performance, band in subject_rows
    )
    weak = tuple(
        item
        for item in subjects
        if item.band == "HIGH_CONCERN"
        or (item.performance_percent is not None and item.performance_percent < 65.0)
    )
    factor_keys = tuple(
        dict.fromkeys(
            [item.key for item in top_factors]
            + list(extra_factor_keys or [])
            + [item.metric for item in warnings if item.metric]
        )
    )
    return StudentAcademicContext(
        overall_attendance_percent=_round_or_none(overall_attendance_percent),
        subjects=subjects,
        risk_score=_round_or_none(risk_score),
        risk_level=risk_level,
        data_completeness=round1(data_completeness),
        top_factors=tuple(top_factors),
        weak_subjects=weak,
        trends=tuple(trends),
        warnings=tuple(warnings),
        study_hours_per_day=study_hours_per_day,
        self_confidence=self_confidence,
        factor_keys=factor_keys,
    )


_PII_PATTERNS = (
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    re.compile(r"\bstudent_id\b", re.I),
    re.compile(r"\buser_id\b", re.I),
    re.compile(r"\bstudent_code\b", re.I),
)


def assert_no_pii(context: StudentAcademicContext, forbidden: list[str]) -> None:
    blob = context.to_prompt_json().lower()
    for pattern in _PII_PATTERNS:
        if pattern.search(blob):
            raise AssertionError(f"context contains PII pattern {pattern.pattern}")
    for item in forbidden:
        if item and item.lower() in blob:
            raise AssertionError(f"context contains forbidden token {item!r}")
