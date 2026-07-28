from datetime import date

from ch_at_a_glance.derive import IndicatorSnapshot
from ch_at_a_glance.web.render import build_cards, render_index_html

_SNAPSHOT = IndicatorSnapshot(
    slug="cpi-inflation",
    label="Inflation",
    category="Economy",
    unit="%",
    note="Test note",
    source_url="https://example.com/data.csv",
    now=1.2,
    change={"1y": 0.3, "2y": None, "5y": None},
    colour={"1y": "red", "2y": "grey", "5y": "grey"},
    data=[(date(2024, 1, 1), 1.0), (date(2025, 1, 1), 1.2)],
)


def test_build_cards_includes_sparkline() -> None:
    cards = build_cards([_SNAPSHOT])

    assert len(cards) == 1
    assert cards[0]["slug"] == "cpi-inflation"
    assert "<svg" in cards[0]["sparkline"]


def test_render_index_html_embeds_indicator_values() -> None:
    html = render_index_html([_SNAPSHOT])

    assert "Inflation" in html
    assert "1.20%" in html
    assert "<svg" in html


def test_large_values_get_thousands_separators_and_no_decimals() -> None:
    snapshot = IndicatorSnapshot(
        slug="job-vacancies",
        label="Job vacancies",
        category="Economy",
        unit="",
        note="Test note",
        source_url="https://example.com/data.csv",
        now=98215.42,
        change={"1y": 4664.36, "2y": None, "5y": None},
        colour={"1y": "green", "2y": "grey", "5y": "grey"},
        data=[(date(2024, 1, 1), 90000.0), (date(2025, 1, 1), 98215.42)],
    )

    cards = build_cards([snapshot])

    assert cards[0]["now_display"] == "98,215"
    assert cards[0]["change_display"]["1y"] == "+4,664"


def test_headline_and_change_share_the_same_decimal_precision() -> None:
    # A count in the thousands (no decimals) with a sub-1000 change (which
    # would independently round to 2dp) must still match the headline's
    # precision, not its own magnitude.
    snapshot = IndicatorSnapshot(
        slug="prison-population",
        label="Prison population",
        category="Crime",
        unit="",
        note="Test note",
        source_url="https://example.com/data.csv",
        now=5434.0,
        change={"1y": 162.0, "2y": None, "5y": None},
        colour={"1y": "grey", "2y": "grey", "5y": "grey"},
        data=[(date(2024, 1, 1), 5272.0), (date(2025, 1, 1), 5434.0)],
    )

    cards = build_cards([snapshot])

    assert cards[0]["now_display"] == "5,434"
    assert cards[0]["change_display"]["1y"] == "+162"
