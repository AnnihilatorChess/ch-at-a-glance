import respx
from httpx import Response

from ch_at_a_glance.collectors.bfs import (
    _GDP_GROWTH_CSV_URL,
    _POPULATION_COMPONENTS_CSV_URL,
    _UNEMPLOYMENT_CSV_URL,
    _WAGE_INDEX_CSV_URL,
    fetch_gdp_growth,
    fetch_net_migration,
    fetch_real_wages,
    fetch_unemployment_rate,
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

_GDP_CSV = (
    '"PERIOD","INDICATOR","UNIT_MEA","VALUE","OBS_STATUS"\n'
    '"2023","GDP per capita at previous year\'s prices","%","1.2","R"\n'
    '"2023","Labour productivity in actual hours worked","%","0.5","R"\n'
    '"2024","GDP per capita at previous year\'s prices","%","0.8","R"\n'
)

_UNEMPLOYMENT_CSV = (
    '"TIME_PERIOD","GEO","ERWP","ERWL","POP1564","UNIT_MEA","OBS_VALUE","OBS_CONFIDENCE","OBS_STATUS"\n'
    '"2023",CH,Total,1,1,pers in %,4.90,0.11,A\n'
    '"2023",CH011,Total,1,1,pers in %,3.20,0.20,A\n'
    '"2023",CH,Total,1,1,pers,220000,2.1,A\n'
    '"2024",CH,Total,1,1,pers in %,5.14,0.11,A\n'
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


@respx.mock
def test_fetch_gdp_growth_filters_to_gdp_per_capita_indicator() -> None:
    respx.get(_GDP_GROWTH_CSV_URL).mock(return_value=Response(200, content=_GDP_CSV.encode()))

    observations = fetch_gdp_growth()

    assert len(observations) == 2
    assert observations[0].date.isoformat() == "2023-01-01"
    assert observations[0].value == 1.2
    assert observations[1].value == 0.8


@respx.mock
def test_fetch_unemployment_rate_filters_to_national_percentage_series() -> None:
    respx.get(_UNEMPLOYMENT_CSV_URL).mock(
        return_value=Response(200, content=_UNEMPLOYMENT_CSV.encode())
    )

    observations = fetch_unemployment_rate()

    assert len(observations) == 2
    assert observations[0].date.isoformat() == "2023-01-01"
    assert observations[0].value == 4.90
    assert observations[1].value == 5.14
