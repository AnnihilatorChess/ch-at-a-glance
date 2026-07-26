# ch-at-a-glance

A "Switzerland at a glance" dashboard, in the spirit of The Times' [Britain at a glance](https://www.thetimes.com/data): a grid of national indicators (economy, living standards, housing, health, crime, immigration), each with a current value, a trend colour, and a sparkline.

Personal project, private, work in progress. See [`docs/DESIGN.md`](docs/DESIGN.md) for the research phase (reverse-engineering the Times pipeline, mapping indicators to Swiss data sources) and [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the system design and the reasoning behind it.

## Stack

Python 3.12, uv, SQLAlchemy 2.0 + Alembic, SQLite (Postgres-ready), httpx, typer, FastAPI + Jinja2 for the frontend, ruff, mypy strict, pytest.

## Status

Early scaffolding. Data pipeline covers a handful of representative Swiss indicators (BFS PxWeb API) to prove the architecture; not yet the full indicator set from the design doc.

## Usage

```bash
uv sync
uv run ch-dashboard update    # pull latest data for all registered indicators
uv run ch-dashboard export    # write a static JSON snapshot (Times-style artifact)
uv run ch-dashboard serve     # run the minimal FastAPI frontend
```
