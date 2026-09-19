import json

from tests.ai.helpers import sample_context, valid_advice_json, valid_advice_payload

from app.ai.validators import validate_analysis_output


def test_valid_output_accepted() -> None:
    context = sample_context()
    outcome = validate_analysis_output(
        valid_advice_json(context, include_numbers=True), context
    )
    assert outcome.ok
    assert outcome.advice is not None


def test_invalid_json_rejected() -> None:
    outcome = validate_analysis_output("not-json", sample_context())
    assert outcome.reason == "INVALID_OUTPUT"


def test_missing_field_rejected() -> None:
    payload = valid_advice_payload()
    del payload["summary"]
    outcome = validate_analysis_output(json.dumps(payload), sample_context())
    assert outcome.reason == "INVALID_OUTPUT"


def test_wrong_enum_rejected() -> None:
    payload = valid_advice_payload()
    payload["priority"] = "URGENT"
    outcome = validate_analysis_output(json.dumps(payload), sample_context())
    assert outcome.reason == "INVALID_OUTPUT"


def test_unknown_factor_rejected() -> None:
    payload = valid_advice_payload()
    payload["main_concerns"][0]["factor"] = "mood"
    outcome = validate_analysis_output(json.dumps(payload), sample_context())
    assert outcome.reason == "INVALID_OUTPUT"


def test_hallucinated_percentage_ungrounded() -> None:
    payload = valid_advice_payload()
    payload["summary"] = "Attendance is 99%."
    outcome = validate_analysis_output(json.dumps(payload), sample_context())
    assert outcome.reason == "UNGROUNDED_OUTPUT"
