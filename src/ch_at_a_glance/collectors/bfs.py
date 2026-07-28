"""Swiss Federal Statistical Office (BFS) collector.

BFS's PxWeb API endpoint exists but its query endpoints reject every standard
PxWeb request pattern we tried (see docs/DESIGN.md), likely broken or
non-standard on their side. The reliable path is opendata.swiss (CKAN) asset
downloads, which BFS publishes as versioned XLS/CSV snapshots rather than a
live feed. That means these collectors can lag the current STAT-TAB figures;
worth revisiting if BFS ever exposes a working query API. A browser-like
User-Agent is required on every request here, opendata.swiss 403s without one.
"""

from __future__ import annotations

import csv
import datetime as dt
from io import BytesIO, StringIO

import httpx
import openpyxl

from ch_at_a_glance.collectors.base import RawObservation, fetch_with_retry

_HEADERS = {"User-Agent": "ch-at-a-glance/0.1 (personal project, non-commercial)"}

# "LIK (Dezember 2015=100), Detailresultate seit 1982".
_CPI_DETAIL_XLSX_URL = "https://dam-api.bfs.admin.ch/hub/api/dam/assets/15964066/master"
_CPI_TOTAL_LABEL_COLUMN = 5
_CPI_FIRST_DATA_COLUMN = 7

# "Schweizerischer Lohnindex, Index und Veraenderung, Basis 2015=100, NOGA08".
_WAGE_INDEX_CSV_URL = "https://dam-api.bfs.admin.ch/hub/api/dam/assets/36506630/master"

# "Straf- und Massnahmenvollzug: Einweisungen, mittlerer Bestand, Aufenthaltstage".
_PRISON_XLSX_URL = "https://dam-api.bfs.admin.ch/hub/api/dam/assets/36199314/master"

# "Komponenten der Entwicklung der staendigen Wohnbevoelkerung, 1861-2024".
_POPULATION_COMPONENTS_CSV_URL = "https://dam-api.bfs.admin.ch/hub/api/dam/assets/36073931/master"


def _fetch_csv_rows(url: str) -> list[dict[str, str]]:
    with httpx.Client(timeout=30.0, headers=_HEADERS, follow_redirects=True) as client:
        response = fetch_with_retry(client, "GET", url)
    text = response.content.decode("utf-8-sig")
    return list(csv.DictReader(StringIO(text)))


def _fetch_workbook(url: str) -> openpyxl.Workbook:
    with httpx.Client(timeout=30.0, headers=_HEADERS, follow_redirects=True) as client:
        response = fetch_with_retry(client, "GET", url)
    return openpyxl.load_workbook(BytesIO(response.content), data_only=True)


def fetch_cpi_inflation() -> list[RawObservation]:
    """Swiss CPI, change vs. same month previous year, monthly, headline ("Total") row.

    Source sheet `VAR_m-12` in BFS's LIK detail workbook: one row per basket
    category, one column per month, values already expressed as % change.
    """
    workbook = _fetch_workbook(_CPI_DETAIL_XLSX_URL)
    sheet = workbook["VAR_m-12"]
    rows = list(sheet.iter_rows(values_only=True))
    header_row = rows[3]
    total_row = next(row for row in rows[4:] if row[_CPI_TOTAL_LABEL_COLUMN] == "Total")

    observations: list[RawObservation] = []
    for header_value, value in zip(
        header_row[_CPI_FIRST_DATA_COLUMN:], total_row[_CPI_FIRST_DATA_COLUMN:], strict=True
    ):
        if not isinstance(header_value, dt.datetime) or not isinstance(value, int | float):
            continue
        observations.append(
            RawObservation(date=header_value.date().replace(day=1), value=float(value))
        )
    return observations


def fetch_real_wages() -> list[RawObservation]:
    """Swiss Wage Index, real (inflation-adjusted), whole economy, annual.

    Filters the CSV to SECTION "B-S" (all NOGA sections, i.e. whole economy),
    SEX "T" (total), WAGE_TYPE "R" (real, as opposed to "N" nominal).
    """
    rows = _fetch_csv_rows(_WAGE_INDEX_CSV_URL)
    observations: list[RawObservation] = []
    for row in rows:
        if row["SECTION"] != "B-S" or row["SEX"] != "T" or row["WAGE_TYPE"] != "R":
            continue
        observations.append(
            RawObservation(date=dt.date(int(row["YEAR"]), 1, 1), value=float(row["VALUE"]))
        )
    return observations


def fetch_prison_population() -> list[RawObservation]:
    """Average daily prison population ("effectif moyen"), annual.

    Source sheet `DATA`: one row per year, column index 2 is the average
    population; the first three rows are titles/headers, not data.
    """
    workbook = _fetch_workbook(_PRISON_XLSX_URL)
    sheet = workbook["DATA"]
    observations: list[RawObservation] = []
    for row in sheet.iter_rows(values_only=True):
        if not isinstance(row[0], int) or not isinstance(row[2], int | float):
            continue
        observations.append(RawObservation(date=dt.date(row[0], 1, 1), value=float(row[2])))
    return observations


def fetch_net_migration() -> list[RawObservation]:
    """Net migration, annual, from BFS's population change components series."""
    rows = _fetch_csv_rows(_POPULATION_COMPONENTS_CSV_URL)
    observations: list[RawObservation] = []
    for row in rows:
        if row["POPULATION_CHANGE_COMPONENT"] != "NMIG":
            continue
        observations.append(
            RawObservation(date=dt.date(int(row["YEAR"]), 1, 1), value=float(row["VALUE"]))
        )
    return observations
