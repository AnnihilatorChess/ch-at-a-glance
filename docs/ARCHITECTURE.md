# Architecture

Phase 2 deliverable. See `docs/DESIGN.md` for the Phase 1 research (Times pipeline reverse-engineering, Swiss indicator mapping, feasibility table).

## Guiding decision

The Times' own "backend" is a scheduled R script overwriting two static JSON files — no live query API, no database. We deliberately build more than that (SQLite + ORM) because it buys history, debuggability, and a real query layer, but the design stays honest about which parts are inherent complexity vs which parts we added on purpose.

## Layers

```
src/ch_at_a_glance/
  config.py       # single source of truth: the indicator registry
  db.py           # engine/session factory, swappable via DATABASE_URL
  models.py       # SQLAlchemy ORM: Indicator, Observation
  collectors/     # one module per data source (bfs.py, snb.py, ...)
    base.py       # Collector protocol + shared retry/backoff helper
  pipeline.py     # orchestrates collectors -> normalize -> upsert
  derive.py       # computes latest value + 1/2/5yr change + colour, at read time
  export.py       # optional: dumps derive.py output as static JSON (Times-parity artifact)
  cli.py          # typer entrypoint: update / export / serve
  web/
    app.py        # FastAPI: JSON endpoint + minimal HTML view
    templates/
alembic/          # schema migrations
tests/
```

## Key decisions and why

**Indicator registry is data, not code branching.** `config.py` holds a list of `IndicatorDefinition` (slug, label, category, unit, direction `good`/`bad`/`neutral`, note, collector reference). Adding indicator #16 means adding one entry plus a collector function, not touching the pipeline, storage, or frontend. This mirrors the Times' own pattern (`up` direction hardcoded per indicator) but keeps it in Python instead of scattered across an R script.

**Derived fields are computed at read time, not stored.** The Times precomputes `change`/`change2`/`change5`/`colour` once per pipeline run because their output *is* the static JSON. We store only raw `(indicator, date, value)` observations and compute the deltas + colours in `derive.py` whenever the frontend asks. This is simpler to reason about (one source of truth: the raw series), makes backfills/corrections trivial (no recompute-and-redeploy step), and costs nothing at this data volume (a few thousand rows per indicator at most).

**SQLAlchemy 2.0 typed ORM over raw SQL.** Widely used, typed `Mapped[...]` style works cleanly with mypy strict, and the same model layer works unchanged against SQLite now and Postgres later — the migration is a connection-string change plus `pip install psycopg2`, not a rewrite. Chose SQLAlchemy over encode/databases or a bare `sqlite3` because the explicit ask was "easy migration to Postgres" and an ORM is the standard way to get that.

**Alembic for migrations, from day one.** Even though the schema is currently two tables, starting with an ORM but without migrations is how projects end up hand-editing SQLite files. One `alembic upgrade head` command works identically against SQLite today and Postgres after the swap.

**Collectors are a `Protocol`, not a base class.** `Collector = Callable[[], list[RawObservation]]`-shaped. Each data source (BFS PxWeb, SNB, SECO scraping, ...) is a plain function returning normalized rows. No inheritance hierarchy to fight when a new source doesn't fit the mold (e.g. SECO has no API and needs an xlsx parser instead of an HTTP client) — see [[OEBB Fare Finder]] for the same lesson learned the hard way with over-abstracted transport layers.

**Failures are per-collector, not pipeline-fatal.** `pipeline.py` wraps each collector call in try/except, logs the failure with the indicator slug and exception, and continues to the next indicator. A dead SECO endpoint on a given day shouldn't block the CPI update.

**Typer + Rich for the CLI.** Mature, typed, minimal boilerplate; matches the pattern already used in [[OEBB Fare Finder]].

**FastAPI for the frontend backend.** Already a dependency-light choice that gives us both a JSON API (`/api/indicators`) and a server-rendered minimal HTML view via Jinja2, without needing a separate JS build step for the Phase 5 validation frontend. The real Times-style frontend (sparklines, filters, category chips) can replace the templates later without touching the data layer.

## Migration path to Postgres

1. Stand up a Postgres instance (local or hosted).
2. Set `DATABASE_URL=postgresql+psycopg2://...` instead of the SQLite default.
3. `uv add psycopg2-binary`.
4. `alembic upgrade head` against the new database.
5. No application code changes — `db.py` reads the URL from environment, `models.py` and `pipeline.py` are dialect-agnostic SQLAlchemy.
