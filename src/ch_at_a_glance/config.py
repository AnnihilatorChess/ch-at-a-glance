"""The indicator registry — the single source of truth for what the dashboard
tracks. Adding an indicator means adding one entry here plus a collector
function; nothing else in the pipeline, storage, or frontend needs to change.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from ch_at_a_glance.collectors import bfe, bfs, cantonal, efv, snb
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
    "Environment",
]


@dataclass(frozen=True, slots=True)
class IndicatorDefinition:
    slug: str
    label: str
    category: Category
    unit: str
    direction: Direction
    note: str
    source_url: str
    collector: Collector


INDICATOR_REGISTRY: list[IndicatorDefinition] = [
    IndicatorDefinition(
        slug="cpi-inflation",
        label="Inflation",
        category="Economy",
        unit="%",
        direction="bad",
        note="Consumer price index, change versus the same month a year earlier.",
        source_url="https://opendata.swiss/en/dataset/landesindex-der-konsumentenpreise",
        collector=bfs.fetch_cpi_inflation,
    ),
    IndicatorDefinition(
        slug="bond-yield-10y",
        label="10-year government bond yield",
        category="Government",
        unit="%",
        direction="bad",
        note="Yield on 10-year Swiss Confederation bond issues, monthly.",
        source_url="https://data.snb.ch/en",
        collector=snb.fetch_10y_bond_yield,
    ),
    IndicatorDefinition(
        slug="policy-rate",
        label="SNB policy rate",
        category="Living Standards",
        unit="%",
        direction="bad",
        note="Swiss National Bank policy rate, updated daily.",
        source_url="https://data.snb.ch/en",
        collector=snb.fetch_policy_rate,
    ),
    IndicatorDefinition(
        slug="real-wages",
        label="Real wages",
        category="Living Standards",
        unit=" index",
        direction="good",
        note="Real (inflation-adjusted) wage index for the whole economy, annual.",
        source_url="https://www.bfs.admin.ch/asset/de/ts-x-03.04.03.00.05",
        collector=bfs.fetch_real_wages,
    ),
    IndicatorDefinition(
        slug="prison-population",
        label="Prison population",
        category="Crime",
        unit="",
        direction="neutral",
        note="Average daily prison population, annual.",
        source_url="https://www.bfs.admin.ch/asset/de/je-d-19.04.02.02",
        collector=bfs.fetch_prison_population,
    ),
    IndicatorDefinition(
        slug="net-migration",
        label="Net migration",
        category="Immigration",
        unit="",
        direction="neutral",
        note="Net migration, immigration minus emigration, annual.",
        source_url="https://www.bfs.admin.ch/asset/de/ts-x-01.02.04.05-a",
        collector=bfs.fetch_net_migration,
    ),
    IndicatorDefinition(
        slug="gdp-growth",
        label="Real GDP per capita growth",
        category="Economy",
        unit="%",
        direction="good",
        note="Real GDP per capita, change on the previous year.",
        source_url="https://www.bfs.admin.ch/asset/de/ts-x-04.02.01.06",
        collector=bfs.fetch_gdp_growth,
    ),
    IndicatorDefinition(
        slug="unemployment-rate",
        label="Unemployment rate",
        category="Economy",
        unit="%",
        direction="bad",
        note="Unemployment rate under the ILO/SAKE definition, national, annual.",
        source_url="https://www.bfs.admin.ch/asset/de/ts-x-40.02.03.02.03",
        collector=bfs.fetch_unemployment_rate,
    ),
    IndicatorDefinition(
        slug="gross-debt-ratio",
        label="Federal gross debt ratio",
        category="Government",
        unit="%",
        direction="bad",
        note="Federal gross debt as a share of GDP, annual.",
        source_url="https://www.efv.admin.ch/de/open-government-data-de",
        collector=efv.fetch_gross_debt_ratio,
    ),
    IndicatorDefinition(
        slug="job-vacancies",
        label="Job vacancies",
        category="Economy",
        unit="",
        direction="good",
        note="Open job vacancies nationwide, quarterly.",
        source_url="https://www.bfs.admin.ch/asset/de/px-x-0602000000_104",
        collector=bfs.fetch_job_vacancies,
    ),
    IndicatorDefinition(
        slug="hospital-beds",
        label="Hospital beds",
        category="Health",
        unit="",
        direction="neutral",
        note="Total hospital bed capacity nationwide, annual.",
        source_url="https://www.bfs.admin.ch/asset/de/je-d-14.04.01.02",
        collector=bfs.fetch_hospital_beds,
    ),
    IndicatorDefinition(
        slug="house-prices-zurich",
        label="House prices (Zurich)",
        category="Housing",
        unit=" CHF",
        direction="bad",
        note=(
            "Median sale price of single-family houses in canton Zurich, annual "
            "(no national house price index exists as open data)."
        ),
        source_url="https://opendata.swiss/en/dataset/immobilienpreise-im-kanton-zurich",
        collector=cantonal.fetch_house_prices_zurich,
    ),
    IndicatorDefinition(
        slug="rent-zug",
        label="Renting a 2-room flat (Zug)",
        category="Housing",
        unit=" CHF/month",
        direction="bad",
        note=(
            "Median net rent for a 2-room apartment in canton Zug, quarterly "
            "(no national rent series exists as open data)."
        ),
        source_url="https://opendata.swiss/en/dataset/nettomiete-fur-wohnungen-nach-zimmerzahl",
        collector=cantonal.fetch_rent_zug,
    ),
    IndicatorDefinition(
        slug="life-expectancy",
        label="Life expectancy at birth",
        category="Health",
        unit=" years",
        direction="good",
        note="Life expectancy at birth, averaged across men and women, annual.",
        source_url="https://www.bfs.admin.ch/asset/de/je-d-01.04.02.03.01",
        collector=bfs.fetch_life_expectancy,
    ),
    IndicatorDefinition(
        slug="co2-emissions",
        label="Greenhouse gas emissions",
        category="Environment",
        unit=" Mt CO2-eq",
        direction="bad",
        note="Total greenhouse gas emissions across all sectors, CO2-equivalent, annual.",
        source_url="https://www.bfs.admin.ch/asset/de/je-d-02.03.02.03",
        collector=bfs.fetch_co2_emissions,
    ),
    IndicatorDefinition(
        slug="hydropower-share",
        label="Hydropower share of electricity",
        category="Environment",
        unit="%",
        direction="good",
        note=(
            "Hydropower's share of net electricity production, annual "
            "(not a full renewable share)."
        ),
        source_url="https://opendata.swiss/en/dataset/schweizerische-elektrizitatsbilanz-jahreswerte",
        collector=bfe.fetch_hydropower_share,
    ),
]
