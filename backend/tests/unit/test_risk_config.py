from dataclasses import replace

import pytest

from app.engines.risk_config import (
    CONFIG,
    RiskConfigError,
    default_config,
    round1,
    validate_config,
)


def test_default_weights_sum_to_one() -> None:
    assert abs(sum(CONFIG.weights.values()) - 1.0) < 1e-12
    validate_config(CONFIG)


def test_round1_half_up() -> None:
    assert round1(1.25) == 1.3
    assert round1(34.375) == 34.4
    assert round1(18.75) == 18.8
    assert round1(67.0625) == 67.1


def test_r11_weights_must_sum_to_one() -> None:
    bad = replace(default_config(), weights={**CONFIG.weights, "attendance": 0.30})
    with pytest.raises(RiskConfigError, match="sum"):
        validate_config(bad)
