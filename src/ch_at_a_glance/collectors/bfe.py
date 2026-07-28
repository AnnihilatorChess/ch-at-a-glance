"""Federal Office of Energy (Bundesamt fuer Energie, BFE) collector.

BFE publishes Switzerland's annual electricity balance as a direct CSV on
its GIS portal, unlike BFS's usual dam-api asset pattern.
"""

from __future__ import annotations

import csv
import datetime as dt
from io import StringIO

import httpx

from ch_at_a_glance.collectors.base import RawObservation, fetch_with_retry

_HEADERS = {"User-Agent": "ch-at-a-glance/0.1 (personal project, non-commercial)"}

# "Schweizerische Elektrizitaetsbilanz - Jahreswerte" (annual electricity balance).
_ELECTRICITY_BALANCE_CSV_URL = (
    "https://www.uvek-gis.admin.ch/BFE/ogd/32/ogd32_elektrizitaetbilanz_jahreswerte.csv"
)


def fetch_hydropower_share() -> list[RawObservation]:
    """Hydropower's share of net electricity production, national, annual, %.

    Uses only "Laufwerk" (run-of-river) and "Speicherwerk" (storage hydro)
    against net production ("Erzeugung_netto_GWh") -- both are unambiguous,
    directly published columns. The CSV's finer "other" breakdown (solar,
    wind, biomass, waste, fossil) doesn't reconcile cleanly against its own
    "other total" column, so a genuine "renewable share" isn't computed here;
    hydropower alone is still a well-defined and, for Switzerland, a very
    large share of production.
    """
    with httpx.Client(timeout=30.0, headers=_HEADERS, follow_redirects=True) as client:
        response = fetch_with_retry(client, "GET", _ELECTRICITY_BALANCE_CSV_URL)
    rows = csv.DictReader(StringIO(response.content.decode("utf-8-sig")))

    observations: list[RawObservation] = []
    for row in rows:
        try:
            run_of_river = float(row["Erzeugung_laufwerk_GWh"])
            storage = float(row["Erzeugung_speicherwerk_GWh"])
            net_production = float(row["Erzeugung_netto_GWh"])
        except ValueError:
            continue
        observations.append(
            RawObservation(
                date=dt.date(int(row["Jahr"]), 1, 1),
                value=(run_of_river + storage) / net_production * 100,
            )
        )
    return observations
