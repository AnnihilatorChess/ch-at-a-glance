"""Federal Finance Administration (Eidgenoessische Finanzverwaltung, EFV) collector.

EFV publishes a genuine machine-readable CSV of the whole federal budget
(the opendata.swiss listing points at an HTML landing page instead, the
real download link had to be found by reading that page).
"""

from __future__ import annotations

import csv
import datetime as dt
from io import StringIO

import httpx

from ch_at_a_glance.collectors.base import RawObservation, fetch_with_retry

_HEADERS = {"User-Agent": "ch-at-a-glance/0.1 (personal project, non-commercial)"}
_FEDERAL_BUDGET_CSV_URL = (
    "https://www.efv.admin.ch/dam/de/sd-web/m9aWXSnsRvNO/bundeshaushalt_de.csv"
)


def fetch_gross_debt_ratio() -> list[RawObservation]:
    """Federal gross debt-to-GDP ratio ("Schuldenquote brutto"), annual.

    The EFV publishes this series several years into the future as budget
    plan figures, not just historical actuals. Those are excluded here so
    the latest value reflects the current year, not a multi-year-out plan.
    """
    with httpx.Client(timeout=30.0, headers=_HEADERS, follow_redirects=True) as client:
        response = fetch_with_retry(client, "GET", _FEDERAL_BUDGET_CSV_URL)

    current_year = dt.date.today().year
    rows = csv.DictReader(StringIO(response.content.decode("utf-8-sig")))
    observations: list[RawObservation] = []
    for row in rows:
        if row["topic"] != "Kennzahlen" or row["variable_name"] != "Schuldenquote brutto":
            continue
        year = int(row["year"])
        if year > current_year:
            continue
        observations.append(RawObservation(date=dt.date(year, 1, 1), value=float(row["value"])))
    return observations
