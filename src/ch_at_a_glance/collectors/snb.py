"""Swiss National Bank data portal collector.

data.snb.ch has a real JSON API (`/api/cube/{cube}/data/json/{lang}`), just
undocumented in any human-readable form — cube IDs were found by testing
against the live API and cross-checking the R `SNBdata` package's examples.
"""

from __future__ import annotations

from datetime import date

import httpx

from ch_at_a_glance.collectors.base import RawObservation, fetch_with_retry

_BOND_YIELD_URL = "https://data.snb.ch/api/cube/rendoblim/data/json/en"


def fetch_10y_bond_yield() -> list[RawObservation]:
    """CHF Swiss Confederation bond issues, 10-year yield, monthly (SNB `rendoblim` cube)."""
    with httpx.Client(timeout=20.0) as client:
        response = fetch_with_retry(client, "GET", _BOND_YIELD_URL, params={"dimSel": "D0(10J)"})

    payload = response.json()
    values = payload["timeseries"][0]["values"]

    observations: list[RawObservation] = []
    for point in values:
        year_str, month_str = point["date"].split("-")
        observations.append(
            RawObservation(date=date(int(year_str), int(month_str), 1), value=float(point["value"]))
        )
    return observations
