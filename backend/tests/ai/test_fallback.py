from tests.ai.helpers import sample_context

from app.ai.fallback import FALLBACK_BANNER, fallback_analysis
from app.ai.validators import validate_analysis_output


def test_fallback_is_valid_and_grounded() -> None:
    context = sample_context()
    advice = fallback_analysis(context)
    assert FALLBACK_BANNER in advice.summary
    assert 1 <= len(advice.main_concerns) <= 5
    assert 3 <= len(advice.recommendations) <= 6
    outcome = validate_analysis_output(advice.model_dump_json(), context)
    assert outcome.ok
