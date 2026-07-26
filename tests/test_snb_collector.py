import respx
from httpx import Response

from ch_at_a_glance.collectors.snb import _BOND_YIELD_URL, fetch_10y_bond_yield


@respx.mock
def test_fetch_10y_bond_yield_parses_snb_response() -> None:
    respx.get(_BOND_YIELD_URL).mock(
        return_value=Response(
            200,
            json={
                "timeseries": [
                    {
                        "header": [{"dim": "Overview", "dimItem": "10 years"}],
                        "metadata": {"key": "EPB@SNB.rendoblim{10J}", "frequency": "P1M"},
                        "values": [
                            {"date": "2025-06", "value": 0.41},
                            {"date": "2025-07", "value": 0.378},
                        ],
                    }
                ]
            },
        )
    )

    observations = fetch_10y_bond_yield()

    assert len(observations) == 2
    assert observations[0].date.isoformat() == "2025-06-01"
    assert observations[0].value == 0.41
    assert observations[1].date.isoformat() == "2025-07-01"
