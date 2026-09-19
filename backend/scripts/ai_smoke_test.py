"""Manual real-API check. Never run in CI. Skips without OPENAI_API_KEY."""

from __future__ import annotations

import json
import sys

from app.ai.client import OpenAIClient
from app.ai.context_builder import (
    FactorFact,
    TrendFact,
    build_context,
)
from app.ai.prompts import analysis_v1
from app.ai.validators import validate_analysis_output
from app.core.config import get_settings


def _sample_context():
    return build_context(
        overall_attendance_percent=64.0,
        subject_rows=[],
        risk_score=84.0,
        risk_level="HIGH",
        data_completeness=1.0,
        top_factors=[
            FactorFact(key="attendance", raw_value=64.0, unit="%", risk=65.0),
            FactorFact(key="internal", raw_value=38.0, unit="%", risk=92.5),
        ],
        trends=[
            TrendFact(series="overall", label="DECLINING", first=72.0, last=55.0)
        ],
        warnings=[],
        study_hours_per_day=1.5,
        self_confidence=2,
        extra_factor_keys=[
            "attendance",
            "internal",
            "assignments",
            "quizzes",
            "previous",
            "study_habits",
        ],
    )


def main() -> int:
    settings = get_settings()
    if not settings.openai_configured:
        print("SKIP: OPENAI_API_KEY is blank. Not calling the provider.")
        return 0

    context = _sample_context()
    client = OpenAIClient(settings)
    result = client.complete(
        analysis_v1.build_messages(context),
        feature="analysis_smoke",
        timeout_seconds=settings.ai_timeout_seconds,
        max_tokens=settings.ai_max_tokens_analysis,
    )
    outcome = validate_analysis_output(result.text, context)
    print(json.dumps({"model": result.model, "raw": result.text}, indent=2))
    if not outcome.ok:
        print(f"INVALID: {outcome.reason}", file=sys.stderr)
        return 1
    print("OK: analysis_v1 output validated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
