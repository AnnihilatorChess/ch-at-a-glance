# ch-at-a-glance

A "Switzerland at a glance" dashboard, in the spirit of The Times' [Britain at a glance](https://www.thetimes.com/data): a grid of national indicators (economy, living standards, housing, health, crime, immigration), each with a current value, a trend colour, and a sparkline.

Personal project, work in progress. See [`docs/DESIGN.md`](docs/DESIGN.md) for the research phase (reverse-engineering the Times pipeline, mapping indicators to Swiss data sources) and [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the system design and the reasoning behind it.

## Stack

Python 3.12, uv, SQLAlchemy 2.0 + Alembic, SQLite (Postgres-ready), httpx, typer, FastAPI + Jinja2 for the frontend, ruff, mypy strict, pytest.

## Status

16 indicators live across Economy, Living Standards, Government, Housing, Health, Crime, Immigration, and Environment: CPI inflation, GDP growth, unemployment rate, real wages, job vacancies, SNB policy rate, 10-year bond yield, federal gross debt ratio, prison population, net migration, hospital beds, life expectancy, CO2 emissions, hydropower share of electricity, and two cantonal proxies (house prices and 2-room rent, both canton-only since no national series exists). Sources are BFS (via opendata.swiss CSV/XLS, its PxWeb API never worked), a hand-rolled parser for one BFS PC-Axis file (job vacancies), SNB's undocumented JSON API, the EFV's federal budget CSV, BFE's electricity balance CSV, and two cantonal open-data portals (Zurich, Zug).

Still missing, no working structured national data source found after a real attempt: housing starts, petrol/diesel/electricity price, PKS shoplifting and other crime-type breakdowns, asylum applications, SNB gold reserves/cash in circulation, national vehicle registrations, consumer confidence, chocolate/wine/cheese production, health insurance premiums, naturalizations, foreign population share. See `docs/DESIGN.md` for what was tried.

## Usage

```bash
uv sync
uv run ch-dashboard update         # pull latest data for all registered indicators
uv run ch-dashboard export         # write a static JSON snapshot (Times-style artifact)
uv run ch-dashboard render-static  # render docs/index.html, the GitHub Pages build
uv run ch-dashboard serve          # run the minimal FastAPI frontend, for local dev/preview
```

## Scheduled updates and GitHub Pages

[`.github/workflows/update-data.yml`](.github/workflows/update-data.yml) runs the pipeline daily (and on manual dispatch): rebuild the database from scratch, pull every indicator, export the JSON snapshot, render the static page, commit whatever changed. There's no cross-run state to persist -- every collector re-fetches its source's full history each time (not just deltas) and the pipeline dedupes by date, so starting from an empty database each run is simpler than caching a SQLite file in CI.

Daily is a deliberate over-poll: source cadences range from daily (SNB rates) to annual (most BFS series), and a run that finds nothing new just logs "0 new" and exits -- see `pipeline.py`.

`data/snapshot.json` and `docs/index.html` are the two generated files tracked in git (everything else generated is gitignored); they're what the workflow commits. GitHub Pages is configured to serve `docs/` from `main`, so the daily commit is also the deploy -- no separate build/deploy step. The FastAPI server (`web/app.py`) stays for local dev only; `web/render.py` renders the same Jinja2 template and SVG sparklines without needing a running server, which is what actually ships to Pages.
