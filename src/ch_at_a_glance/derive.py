"""Computes latest value, 1/2/5-year change, and trend colour at read time.

The database stores only raw (date, value) observations; this module is the
only place that knows how to turn that into the Times-style snapshot shape.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from ch_at_a_glance.models import Indicator, Observation

Colour = str  # "green" | "red" | "grey"

_HORIZONS_DAYS = {"1y": 365, "2y": 730, "5y": 1825}


@dataclass(slots=True)
class IndicatorSnapshot:
    slug: str
    label: str
    category: str
    unit: str
    note: str
    source_url: str
    now: float | None
    change: dict[str, float | None]
    colour: dict[str, Colour]
    data: list[tuple[date, float]]


def _value_as_of(observations: list[Observation], as_of: date) -> float | None:
    """Latest observation on or before `as_of` (carry-forward semantics, matching
    the Times' own forward-fill approach for sparse quarterly/annual series)."""
    candidates = [obs.value for obs in observations if obs.date <= as_of]
    return candidates[-1] if candidates else None


def _colour_for(direction: str, change: float | None) -> Colour:
    if change is None or change == 0 or direction == "neutral":
        return "grey"
    improving = change > 0 if direction == "good" else change < 0
    return "green" if improving else "red"


def snapshot(indicator: Indicator) -> IndicatorSnapshot:
    observations = sorted(indicator.observations, key=lambda o: o.date)
    now_value = observations[-1].value if observations else None
    now_date = observations[-1].date if observations else None

    change: dict[str, float | None] = {}
    colour: dict[str, Colour] = {}
    for key, days in _HORIZONS_DAYS.items():
        if now_date is None:
            change[key] = None
            colour[key] = "grey"
            continue
        past_value = _value_as_of(observations, now_date - timedelta(days=days))
        delta = None if past_value is None or now_value is None else now_value - past_value
        change[key] = delta
        colour[key] = _colour_for(indicator.direction, delta)

    return IndicatorSnapshot(
        slug=indicator.slug,
        label=indicator.label,
        category=indicator.category,
        unit=indicator.unit,
        note=indicator.note,
        source_url=indicator.source_url,
        now=now_value,
        change=change,
        colour=colour,
        data=[(obs.date, obs.value) for obs in observations],
    )
