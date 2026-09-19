from __future__ import annotations

from app.models.enums import ProgressDirection

UNCHANGED_THRESHOLD = 2.0
PROGRESS_NOTE = (
    "This shows the observed change in risk since the intervention was "
    "created. It does not prove the intervention caused it."
)


def progress_change(
    current_score: float | None, baseline_score: float | None
) -> float | None:
    if current_score is None or baseline_score is None:
        return None
    return current_score - baseline_score


def progress_direction(
    change: float | None, threshold: float = UNCHANGED_THRESHOLD
) -> ProgressDirection:
    if change is None or abs(change) < threshold:
        return ProgressDirection.UNCHANGED
    if change < 0:
        return ProgressDirection.IMPROVED
    return ProgressDirection.WORSENED
