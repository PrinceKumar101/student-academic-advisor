from app.engines.intervention_progress import progress_change, progress_direction
from app.models.enums import ProgressDirection


def test_direction_thresholds() -> None:
    assert progress_direction(-2.0) is ProgressDirection.IMPROVED
    assert progress_direction(-1.9) is ProgressDirection.UNCHANGED
    assert progress_direction(0) is ProgressDirection.UNCHANGED
    assert progress_direction(1.9) is ProgressDirection.UNCHANGED
    assert progress_direction(2.0) is ProgressDirection.WORSENED
    assert progress_direction(None) is ProgressDirection.UNCHANGED


def test_change_requires_both_scores() -> None:
    assert progress_change(63.0, 84.0) == -21.0
    assert progress_change(None, 84.0) is None
    assert progress_change(63.0, None) is None
