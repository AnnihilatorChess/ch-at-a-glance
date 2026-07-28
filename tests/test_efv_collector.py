from datetime import date

import respx
from httpx import Response

from ch_at_a_glance.collectors.efv import _FEDERAL_BUDGET_CSV_URL, fetch_gross_debt_ratio

_FAR_FUTURE_YEAR = date.today().year + 3

_BUDGET_CSV = (
    "topic,variable_id,variable_name,unit,year,value\n"
    "Kennzahlen,10,Schuldenquote brutto,%,2024,15.16\n"
    "Kennzahlen,10,Schuldenquote brutto,%,2025,14.81\n"
    f"Kennzahlen,10,Schuldenquote brutto,%,{_FAR_FUTURE_YEAR},14.54\n"
    "Kennzahlen,11,Schuldenquote netto,%,2024,10.0\n"
)


@respx.mock
def test_fetch_gross_debt_ratio_excludes_years_beyond_today() -> None:
    respx.get(_FEDERAL_BUDGET_CSV_URL).mock(
        return_value=Response(200, content=_BUDGET_CSV.encode())
    )

    observations = fetch_gross_debt_ratio()

    years = [o.date.year for o in observations]
    assert years == [2024, 2025]
    assert _FAR_FUTURE_YEAR not in years
    assert observations[-1].value == 14.81
