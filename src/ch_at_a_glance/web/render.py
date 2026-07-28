"""Card-building and HTML rendering shared by the live FastAPI route and the
static GitHub Pages build. Kept separate from a Starlette/FastAPI Request so
the same template can be rendered outside a running server.
"""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import jinja2

from ch_at_a_glance.derive import IndicatorSnapshot
from ch_at_a_glance.web.charts import sparkline_svg

_TEMPLATES_DIR = Path(__file__).parent / "templates"
_env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(_TEMPLATES_DIR)), autoescape=True)


def _arrow(change: float | None) -> str:
    if not change:
        return ""
    return "↑" if change > 0 else "↓"


def _decimals_for(now: float) -> int:
    """Large counts read as whole numbers; small rates/indices/percentages
    need their precision. Decided once per indicator from its current value
    so the headline number and its change always agree on precision."""
    return 0 if abs(now) >= 1000 else 2  # noqa: PLR2004


def _format_number(value: float, decimals: int) -> str:
    return f"{value:,.{decimals}f}"


def _format_change(value: float, decimals: int) -> str:
    sign = "+" if value >= 0 else "-"
    return f"{sign}{_format_number(abs(value), decimals)}"


def build_cards(snapshots: list[IndicatorSnapshot]) -> list[dict[str, object]]:
    cards = []
    for s in snapshots:
        card = asdict(s)
        card["sparkline"] = sparkline_svg(s.data, colour=s.colour["1y"])
        card["arrow"] = {key: _arrow(value) for key, value in s.change.items()}
        decimals = _decimals_for(s.now) if s.now is not None else 2
        card["now_display"] = _format_number(s.now, decimals) if s.now is not None else None
        card["change_display"] = {
            key: (_format_change(value, decimals) if value is not None else None)
            for key, value in s.change.items()
        }
        cards.append(card)
    return cards


def build_context(snapshots: list[IndicatorSnapshot]) -> dict[str, object]:
    return {
        "cards": build_cards(snapshots),
        "better": sum(1 for s in snapshots if s.colour["1y"] == "green"),
        "worse": sum(1 for s in snapshots if s.colour["1y"] == "red"),
    }


def render_index_html(snapshots: list[IndicatorSnapshot]) -> str:
    template = _env.get_template("index.html")
    return template.render(**build_context(snapshots))
