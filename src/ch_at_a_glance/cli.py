"""Typer entrypoint: update / export / serve."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table
from sqlalchemy import select

from ch_at_a_glance.db import session_scope
from ch_at_a_glance.derive import snapshot
from ch_at_a_glance.models import Indicator
from ch_at_a_glance.pipeline import run_update

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

app = typer.Typer(help="Switzerland at a glance: data pipeline and dashboard")
console = Console()


@app.command()
def update() -> None:
    """Pull latest data for every registered indicator."""
    results = run_update()
    table = Table("Indicator", "Result")
    for slug, status in results.items():
        table.add_row(slug, status)
    console.print(table)


@app.command()
def export(output: Path = Path("data/snapshot.json")) -> None:
    """Write a static JSON snapshot of all indicators (Times-style artifact)."""
    with session_scope() as session:
        indicators = (
            session.execute(select(Indicator).order_by(Indicator.category, Indicator.label))
            .scalars()
            .all()
        )
        snapshots = [snapshot(ind) for ind in indicators]

    payload = [
        {
            "slug": s.slug,
            "label": s.label,
            "parent": s.category,
            "unit": s.unit,
            "note": s.note,
            "now": s.now,
            "change": s.change["1y"],
            "change2": s.change["2y"],
            "change5": s.change["5y"],
            "colour": s.colour["1y"],
            "colour2": s.colour["2y"],
            "colour5": s.colour["5y"],
            "data": [{d.isoformat(): v} for d, v in s.data],
        }
        for s in snapshots
    ]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2))
    console.print(f"Wrote {len(payload)} indicator(s) to {output}")


@app.command()
def serve(host: str = "127.0.0.1", port: int = 8000, reload: bool = False) -> None:
    """Run the minimal FastAPI frontend."""
    import uvicorn

    uvicorn.run("ch_at_a_glance.web.app:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    app()
