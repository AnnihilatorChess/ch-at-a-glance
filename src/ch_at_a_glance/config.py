"""The indicator registry — the single source of truth for what the dashboard
tracks. Adding an indicator means adding one entry here plus a collector
function; nothing else in the pipeline, storage, or frontend needs to change.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from ch_at_a_glance.collectors import bfs, snb
from ch_at_a_glance.collectors.base import Collector

Direction = Literal["good", "bad", "neutral"]
Category = Literal[
    "Economy",
    "Living Standards",
    "Housing",
    "Health",
    "Crime",
    "Immigration",
    "Government",
]


@dataclass(frozen=True, slots=True)
class IndicatorDefinition:
    slug: str
    label: str
    category: Category
    unit: str
    direction: Direction
    note: str
    collector: Collector


INDICATOR_REGISTRY: list[IndicatorDefinition] = [
    IndicatorDefinition(
        slug="cpi-inflation",
        label="Inflation",
        category="Economy",
        unit="%",
        direction="bad",
        note=(
            "Consumer price index, change vs. same month previous year "
            "(BFS, Landesindex der Konsumentenpreise)"
        ),
        collector=bfs.fetch_cpi_inflation,
    ),
    IndicatorDefinition(
        slug="bond-yield-10y",
        label="10-year government bond yield",
        category="Government",
        unit="%",
        direction="bad",
        note="CHF Swiss Confederation bond issues, 10-year yield, monthly (SNB data portal)",
        collector=snb.fetch_10y_bond_yield,
    ),
    IndicatorDefinition(
        slug="policy-rate",
        label="SNB policy rate",
        category="Living Standards",
        unit="%",
        direction="bad",
        note="Swiss National Bank policy rate, daily (SNB data portal)",
        collector=snb.fetch_policy_rate,
    ),
    IndicatorDefinition(
        slug="real-wages",
        label="Real wages",
        category="Living Standards",
        unit=" index",
        direction="good",
        note=(
            "Swiss Wage Index, real (inflation-adjusted), whole economy, base 2015=100, "
            "annual (BFS)"
        ),
        collector=bfs.fetch_real_wages,
    ),
    IndicatorDefinition(
        slug="prison-population",
        label="Prison population",
        category="Crime",
        unit="",
        direction="neutral",
        note="Average daily prison population, annual (BFS, Straf- und Massnahmenvollzug)",
        collector=bfs.fetch_prison_population,
    ),
    IndicatorDefinition(
        slug="net-migration",
        label="Net migration",
        category="Immigration",
        unit="",
        direction="neutral",
        note="Net migration (immigration minus emigration), annual (BFS population statistics)",
        collector=bfs.fetch_net_migration,
    ),
]
