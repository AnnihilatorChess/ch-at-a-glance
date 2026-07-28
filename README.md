# ch-at-a-glance

A "Switzerland at a glance" dashboard, in the spirit of The Times' [Britain at a glance](https://www.thetimes.com/data): a grid of national indicators (economy, living standards, housing, health, crime, immigration), each with a current value, a trend colour, and a sparkline.

Personal project, private, work in progress. See [`docs/DESIGN.md`](docs/DESIGN.md) for the research phase (reverse-engineering the Times pipeline, mapping indicators to Swiss data sources) and [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the system design and the reasoning behind it.

## Stack

Python 3.12, uv, SQLAlchemy 2.0 + Alembic, SQLite (Postgres-ready), httpx, typer, FastAPI + Jinja2 for the frontend, ruff, mypy strict, pytest.

## Status

9 indicators live across Economy, Living Standards, Government, Crime, and Immigration: CPI inflation, GDP growth, unemployment rate, real wages, SNB policy rate, 10-year bond yield, federal gross debt ratio, prison population, net migration. Sources are BFS (via opendata.swiss CSV/XLS, its PxWeb API never worked), SNB's undocumented JSON API, and the EFV's federal budget CSV.

Still missing from the design doc's v1 list, no working structured data source found after a real attempt: house prices, housing starts, petrol price, job vacancies, PKS shoplifting, asylum applications. See `docs/DESIGN.md` for what was tried.

## Usage

```bash
uv sync
uv run ch-dashboard update    # pull latest data for all registered indicators
uv run ch-dashboard export    # write a static JSON snapshot (Times-style artifact)
uv run ch-dashboard serve     # run the minimal FastAPI frontend
```
