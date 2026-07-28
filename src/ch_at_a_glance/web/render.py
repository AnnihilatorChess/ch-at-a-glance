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


def build_cards(snapshots: list[IndicatorSnapshot]) -> list[dict[str, object]]:
    return [{**asdict(s), "sparkline": sparkline_svg([v for _, v in s.data])} for s in snapshots]


def render_index_html(snapshots: list[IndicatorSnapshot]) -> str:
    template = _env.get_template("index.html")
    return template.render(cards=build_cards(snapshots))
