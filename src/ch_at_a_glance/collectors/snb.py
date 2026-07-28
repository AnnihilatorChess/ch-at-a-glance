"""Swiss National Bank data portal collector.

data.snb.ch has a real JSON API (`/api/cube/{cube}/data/json/{lang}`), just
undocumented anywhere human readable. Cube IDs were found by testing against
the live API and cross-checking the R `SNBdata` package's examples; a wrong
cube ID returns `{"message": "Table {id} not found"}` rather than raising.
"""

from __future__ import annotations

from datetime import date

import httpx

from ch_at_a_glance.collectors.base import RawObservation, fetch_with_retry

_BOND_YIELD_URL = "https://data.snb.ch/api/cube/rendoblim/data/json/en"
_POLICY_RATE_URL = "https://data.snb.ch/api/cube/snbgwdzid/data/json/en"


def _parse_snb_date(date_str: str) -> date:
    """SNB dates come as either "YYYY-MM" (monthly cubes) or "YYYY-MM-DD" (daily cubes)."""
    parts = date_str.split("-")
    if len(parts) == 2:
        year_str, month_str = parts
        return date(int(year_str), int(month_str), 1)
    year_str, month_str, day_str = parts
    return date(int(year_str), int(month_str), int(day_str))


def fetch_10y_bond_yield() -> list[RawObservation]:
    """CHF Swiss Confederation bond issues, 10-year yield, monthly (SNB `rendoblim` cube)."""
    with httpx.Client(timeout=20.0) as client:
        response = fetch_with_retry(client, "GET", _BOND_YIELD_URL, params={"dimSel": "D0(10J)"})

    values = response.json()["timeseries"][0]["values"]
    return [
        RawObservation(date=_parse_snb_date(point["date"]), value=float(point["value"]))
        for point in values
    ]


def fetch_policy_rate() -> list[RawObservation]:
    """SNB policy rate, daily (SNB `snbgwdzid` cube, one of seven series it returns)."""
    with httpx.Client(timeout=20.0) as client:
        response = fetch_with_retry(client, "GET", _POLICY_RATE_URL)

    series = next(
        ts
        for ts in response.json()["timeseries"]
        if ts["header"][0]["dimItem"] == "SNB policy rate"
    )
    return [
        RawObservation(date=_parse_snb_date(point["date"]), value=float(point["value"]))
        for point in series["values"]
    ]
