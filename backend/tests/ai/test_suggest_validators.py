import json

from tests.ai.helpers import sample_context

from app.ai.fallback import fallback_suggestions
from app.ai.validators import validate_suggestions_output


def test_valid_and_ungrounded_suggestions() -> None:
    context = sample_context()
    advice = fallback_suggestions(context)
    assert validate_suggestions_output(advice.model_dump_json(), context).ok

    bad = {
        "suggestions": [
            {
                "title": "Invented",
                "description": "Attendance is 11%.",
                "priority": "HIGH",
                "reason": "Made up.",
            }
        ]
    }
    outcome = validate_suggestions_output(json.dumps(bad), context)
    assert not outcome.ok
    assert outcome.reason == "UNGROUNDED_OUTPUT"
