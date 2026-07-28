# ch-at-a-glance

A "Switzerland at a glance" dashboard, in the spirit of The Times' [Britain at a glance](https://www.thetimes.com/data): a grid of national indicators (economy, living standards, housing, health, crime, immigration), each with a current value, a trend colour, and a sparkline.

Personal project, private, work in progress. See [`docs/DESIGN.md`](docs/DESIGN.md) for the research phase (reverse-engineering the Times pipeline, mapping indicators to Swiss data sources) and [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the system design and the reasoning behind it.

## Stack

Python 3.12, uv, SQLAlchemy 2.0 + Alembic, SQLite (Postgres-ready), httpx, typer, FastAPI + Jinja2 for the frontend, ruff, mypy strict, pytest.

## Status

13 indicators live across Economy, Living Standards, Government, Housing, Health, Crime, and Immigration: CPI inflation, GDP growth, unemployment rate, real wages, job vacancies, SNB policy rate, 10-year bond yield, federal gross debt ratio, prison population, net migration, hospital beds, and two cantonal proxies (house prices and 2-room rent, both canton-only since no national series exists). Sources are BFS (via opendata.swiss CSV/XLS, its PxWeb API never worked), a hand-rolled parser for one BFS PC-Axis file (job vacancies), SNB's undocumented JSON API, the EFV's federal budget CSV, and two cantonal open-data portals (Zurich, Zug).

Still missing, no working structured national data source found after a real attempt: housing starts, petrol/diesel/electricity price, PKS shoplifting and other crime-type breakdowns, asylum applications, SNB gold reserves/cash in circulation, national vehicle registrations, consumer confidence. See `docs/DESIGN.md` for what was tried.

## Usage

```bash
uv sync
uv run ch-dashboard update    # pull latest data for all registered indicators
uv run ch-dashboard export    # write a static JSON snapshot (Times-style artifact)
uv run ch-dashboard serve     # run the minimal FastAPI frontend
```
