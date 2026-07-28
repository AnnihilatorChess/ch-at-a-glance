import respx
from httpx import Response

from ch_at_a_glance.collectors.cantonal import (
    _ZG_RENT_CSV_URL,
    _ZH_HOUSE_PRICES_CSV_URL,
    fetch_house_prices_zurich,
    fetch_rent_zug,
)

_ZH_HOUSE_CSV = (
    '"Jahr","Kantonsnr.","Kanton","region","Verkaeufe","Durchschnitt","Q10","Q25",'
    '"Median","Q75","Q90","Quelle","Indikator"\n'
    '2023,1,"ZH","Stadt Zürich",109,1835173,760000,910000,1381000,1975102,3776000,"x","y"\n'
    '2023,1,"ZH","Ganzer Kanton Zürich",900,1300000,700000,900000,1200000,1500000,2000000,"x","y"\n'
    '2024,1,"ZH","Ganzer Kanton Zürich",950,1350000,720000,920000,1250000,1550000,2100000,"x","y"\n'
)

_ZG_RENT_CSV = (
    '"jahr","quartal","gemeinde","bfscode","zimmerzahl","nettomiete_chf"\n'
    '2024,1,"Baar","1701","2 Zimmer",1400\n'
    '2024,1,"Kanton Zug","1700","1 Zimmer",900\n'
    '2024,1,"Kanton Zug","1700","2 Zimmer",1450\n'
    '2024,2,"Kanton Zug","1700","2 Zimmer",NA\n'
    '2024,3,"Kanton Zug","1700","2 Zimmer",1470\n'
)


@respx.mock
def test_fetch_house_prices_zurich_filters_to_canton_wide_region() -> None:
    respx.get(_ZH_HOUSE_PRICES_CSV_URL).mock(
        return_value=Response(200, content=_ZH_HOUSE_CSV.encode("utf-8-sig"))
    )

    observations = fetch_house_prices_zurich()

    assert len(observations) == 2
    assert observations[0].date.isoformat() == "2023-01-01"
    assert observations[0].value == 1200000.0
    assert observations[1].value == 1250000.0


@respx.mock
def test_fetch_rent_zug_filters_to_canton_wide_two_room_and_skips_na() -> None:
    respx.get(_ZG_RENT_CSV_URL).mock(
        return_value=Response(200, content=_ZG_RENT_CSV.encode("utf-8-sig"))
    )

    observations = fetch_rent_zug()

    assert len(observations) == 2
    assert observations[0].date.isoformat() == "2024-01-01"
    assert observations[0].value == 1450.0
    assert observations[1].date.isoformat() == "2024-07-01"
    assert observations[1].value == 1470.0
