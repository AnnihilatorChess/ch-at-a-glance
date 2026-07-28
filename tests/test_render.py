from datetime import date

from ch_at_a_glance.derive import IndicatorSnapshot
from ch_at_a_glance.web.render import build_cards, render_index_html

_SNAPSHOT = IndicatorSnapshot(
    slug="cpi-inflation",
    label="Inflation",
    category="Economy",
    unit="%",
    note="Test note",
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
