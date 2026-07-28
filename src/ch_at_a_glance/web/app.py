"""Minimal FastAPI frontend. Purpose: validate collected data, not to look
like the final Times-style dashboard yet (see docs/DESIGN.md)."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select

from ch_at_a_glance.db import session_scope
from ch_at_a_glance.derive import IndicatorSnapshot, snapshot
from ch_at_a_glance.models import Indicator
from ch_at_a_glance.web.render import build_cards

app = FastAPI(title="ch-at-a-glance (dev)")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


def _all_snapshots() -> list[IndicatorSnapshot]:
    with session_scope() as session:
        indicators = (
            session.execute(select(Indicator).order_by(Indicator.category, Indicator.label))
            .scalars()
            .all()
        )
        return [snapshot(indicator) for indicator in indicators]


@app.get("/api/indicators")
def api_indicators() -> list[dict[str, object]]:
    return [asdict(s) for s in _all_snapshots()]


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    cards = build_cards(_all_snapshots())
    return templates.TemplateResponse(request, "index.html", {"cards": cards})
