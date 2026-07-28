import respx
from httpx import Response

from ch_at_a_glance.collectors.bfs import (
    _POPULATION_COMPONENTS_CSV_URL,
    _WAGE_INDEX_CSV_URL,
    fetch_net_migration,
    fetch_real_wages,
)

_WAGE_CSV = (
    '"YEAR","SECTION","DIVISION","SEX","WAGE_TYPE","VALUE","VALUE_P","OBS_STATUS_VALUE"\n'
    '"2023","B-S","05 - 96","T","N","105.9","1.7","A"\n'
    '"2023","B-S","05 - 96","T","R","99.5","-0.4","A"\n'
    '"2023","CA","10 - 12","T","R","102.0","0.5","A"\n'
    '"2024","B-S","05 - 96","T","R","100.2","0.7","A"\n'
)

_MIGRATION_CSV = (
    '"YEAR","POPULATION_CHANGE_COMPONENT","VALUE","OBS_STATUS"\n'
    '"2023","NMIG","51000","A"\n'
    '"2023","LIVB","85000","A"\n'
    '"2024","NMIG","49000","A"\n'
)


@respx.mock
def test_fetch_real_wages_filters_to_whole_economy_real_series() -> None:
    respx.get(_WAGE_INDEX_CSV_URL).mock(return_value=Response(200, content=_WAGE_CSV.encode()))

    observations = fetch_real_wages()

    assert len(observations) == 2
    assert observations[0].date.isoformat() == "2023-01-01"
    assert observations[0].value == 99.5
    assert observations[1].date.isoformat() == "2024-01-01"


@respx.mock
def test_fetch_net_migration_filters_to_nmig_component() -> None:
    respx.get(_POPULATION_COMPONENTS_CSV_URL).mock(
        return_value=Response(200, content=_MIGRATION_CSV.encode())
    )

    observations = fetch_net_migration()

    assert len(observations) == 2
    assert observations[0].value == 51000.0
    assert observations[1].value == 49000.0
