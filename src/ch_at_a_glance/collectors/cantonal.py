"""Cantonal open-data collectors.

No genuine national time series exists for house prices or rents (BFS's own
house price index is PDF-only; opendata.swiss has nothing at the national
level either). These collectors use canton-level open data instead -- a real
compromise, not a silent substitution, so indicator labels and notes say
"Zurich" / "Zug" explicitly rather than implying a national figure.
"""

from __future__ import annotations

import csv
import datetime as dt
from io import StringIO

import httpx

from ch_at_a_glance.collectors.base import RawObservation, fetch_with_retry

_HEADERS = {"User-Agent": "ch-at-a-glance/0.1 (personal project, non-commercial)"}

# Canton Zurich: median sale price of single-family houses, by region, annual.
_ZH_HOUSE_PRICES_CSV_URL = (
    "https://daten.statistik.zh.ch/ogd/daten/ressourcen/KTZH_00003158_00006781.csv"
)

# Canton Zug: median net rent by municipality and room count, quarterly.
_ZG_RENT_CSV_URL = "https://data.zg.ch/store/1/resource/339"


def _fetch_csv_rows(url: str) -> list[dict[str, str]]:
    with httpx.Client(timeout=30.0, headers=_HEADERS, follow_redirects=True) as client:
        response = fetch_with_retry(client, "GET", url)
    text = response.content.decode("utf-8-sig")
    return list(csv.DictReader(StringIO(text)))


def fetch_house_prices_zurich() -> list[RawObservation]:
    """Median sale price of single-family houses, canton-wide, annual."""
    rows = _fetch_csv_rows(_ZH_HOUSE_PRICES_CSV_URL)
    observations: list[RawObservation] = []
    for row in rows:
        if row["region"] != "Ganzer Kanton Zürich":
            continue
        observations.append(
            RawObservation(date=dt.date(int(row["Jahr"]), 1, 1), value=float(row["Median"]))
        )
    return observations


def fetch_rent_zug() -> list[RawObservation]:
    """Median net rent for a 2-room apartment, canton-wide, quarterly."""
    rows = _fetch_csv_rows(_ZG_RENT_CSV_URL)
    observations: list[RawObservation] = []
    for row in rows:
        if row["gemeinde"] != "Kanton Zug" or row["zimmerzahl"] != "2 Zimmer":
            continue
        if row["nettomiete_chf"] in ("", "NA"):
            continue
        year, quarter = int(row["jahr"]), int(row["quartal"])
        observations.append(
            RawObservation(
                date=dt.date(year, (quarter - 1) * 3 + 1, 1),
                value=float(row["nettomiete_chf"]),
            )
        )
    return observations
