import respx
from httpx import Response

from ch_at_a_glance.collectors.bfe import _ELECTRICITY_BALANCE_CSV_URL, fetch_hydropower_share

_ELECTRICITY_CSV = (
    "Jahr,Erzeugung_laufwerk_GWh,Erzeugung_speicherwerk_GWh,Erzeugung_kernkraftwerk_GWh,"
    "Erzeugung_netto_GWh\n"
    "1960,NA,NA,NA,20427\n"
    "2024,19403,28934,22983,76237\n"
)


@respx.mock
def test_fetch_hydropower_share_computes_percentage_of_net_production() -> None:
    respx.get(_ELECTRICITY_BALANCE_CSV_URL).mock(
        return_value=Response(200, content=_ELECTRICITY_CSV.encode("utf-8-sig"))
    )

    observations = fetch_hydropower_share()

    assert len(observations) == 1
    assert observations[0].date.isoformat() == "2024-01-01"
    assert round(observations[0].value, 2) == round((19403 + 28934) / 76237 * 100, 2)
