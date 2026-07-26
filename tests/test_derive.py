from datetime import date

from ch_at_a_glance.derive import snapshot
from ch_at_a_glance.models import Indicator, Observation


def _indicator(direction: str, points: list[tuple[date, float]]) -> Indicator:
    indicator = Indicator(
        slug="test-indicator",
        label="Test indicator",
        category="Economy",
        unit="%",
        direction=direction,
        note="A test indicator",
    )
    indicator.observations = [Observation(date=d, value=v) for d, v in points]
    return indicator


def test_snapshot_with_no_observations_returns_nulls() -> None:
    indicator = _indicator("bad", [])
    result = snapshot(indicator)
    assert result.now is None
    assert result.change["1y"] is None
    assert result.colour["1y"] == "grey"


def test_rising_value_is_red_when_direction_is_bad() -> None:
    indicator = _indicator(
        "bad",
        [(date(2025, 1, 1), 2.0), (date(2026, 1, 1), 3.0)],
    )
    result = snapshot(indicator)
    assert result.now == 3.0
    assert result.change["1y"] == 1.0
    assert result.colour["1y"] == "red"


def test_rising_value_is_green_when_direction_is_good() -> None:
    indicator = _indicator(
        "good",
        [(date(2025, 1, 1), 2.0), (date(2026, 1, 1), 3.0)],
    )
    result = snapshot(indicator)
    assert result.colour["1y"] == "green"


def test_neutral_direction_is_always_grey() -> None:
    indicator = _indicator(
        "neutral",
        [(date(2025, 1, 1), 2.0), (date(2026, 1, 1), 3.0)],
    )
    result = snapshot(indicator)
    assert result.colour["1y"] == "grey"


def test_missing_history_leaves_change_none() -> None:
    # Only one observation ever recorded: no 1-year-ago value to diff against.
    indicator = _indicator("bad", [(date(2026, 1, 1), 3.0)])
    result = snapshot(indicator)
    assert result.now == 3.0
    assert result.change["1y"] is None
    assert result.colour["1y"] == "grey"


def test_sparse_series_uses_carry_forward_semantics() -> None:
    # Quarterly data: the "1 year ago" lookup should find the nearest earlier point.
    indicator = _indicator(
        "bad",
        [(date(2025, 1, 1), 1.0), (date(2025, 4, 1), 1.5), (date(2026, 1, 2), 2.0)],
    )
    result = snapshot(indicator)
    assert result.now == 2.0
    # ~1 year before 2026-01-02 falls after 2025-01-01 but before 2025-04-01,
    # so carry-forward should pick the 2025-01-01 value (1.0), not None.
    assert result.change["1y"] == 1.0
