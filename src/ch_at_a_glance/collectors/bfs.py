"""Swiss Federal Statistical Office (BFS) collector.

BFS's PxWeb API endpoint exists but its query endpoints reject every standard
PxWeb request pattern we tried (see docs/DESIGN.md) — likely broken or
non-standard on their side. The reliable path is opendata.swiss (CKAN) asset
downloads, which BFS publishes as versioned XLS snapshots rather than a live
feed. That means this collector can lag the current STAT-TAB figures; worth
revisiting if BFS ever exposes a working query API.
"""

from __future__ import annotations

import datetime as dt
from io import BytesIO

import httpx
import openpyxl

from ch_at_a_glance.collectors.base import RawObservation, fetch_with_retry

# "LIK (Dezember 2015=100), Detailresultate seit 1982" via opendata.swiss/BFS dam-api.
_CPI_DETAIL_XLSX_URL = "https://dam-api.bfs.admin.ch/hub/api/dam/assets/15964066/master"
_HEADERS = {"User-Agent": "ch-at-a-glance/0.1 (personal project, non-commercial)"}
_TOTAL_LABEL_COLUMN = 5
_FIRST_DATA_COLUMN = 7


def fetch_cpi_inflation() -> list[RawObservation]:
    """Swiss CPI, change vs. same month previous year, monthly, headline ("Total") row.

    Source sheet `VAR_m-12` in BFS's LIK detail workbook: one row per basket
    category, one column per month, values already expressed as % change.
    """
    with httpx.Client(timeout=30.0, headers=_HEADERS, follow_redirects=True) as client:
        response = fetch_with_retry(client, "GET", _CPI_DETAIL_XLSX_URL)

    workbook = openpyxl.load_workbook(BytesIO(response.content), data_only=True)
    sheet = workbook["VAR_m-12"]
    rows = list(sheet.iter_rows(values_only=True))
    header_row = rows[3]
    total_row = next(row for row in rows[4:] if row[_TOTAL_LABEL_COLUMN] == "Total")

    observations: list[RawObservation] = []
    for header_value, value in zip(
        header_row[_FIRST_DATA_COLUMN:], total_row[_FIRST_DATA_COLUMN:], strict=True
    ):
        if not isinstance(header_value, dt.datetime) or not isinstance(value, int | float):
            continue
        observations.append(
            RawObservation(date=header_value.date().replace(day=1), value=float(value))
        )
    return observations
