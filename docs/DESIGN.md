# Design Document — Swiss "at a glance" dashboard

Phase 1 deliverable. Reverse-engineered from the actual Times "Britain at a glance" pipeline (their `times/times-channel-britain-at-a-glance-data` GitHub repo, R-based) plus the public thetimes.com/data page. `thetimes.com` is blocked by browsing policy in this environment so the UI description below is built from the screenshot already shared in this conversation, not a live inspection.

## 1. UI / UX

- Header: title ("Britain at a glance"), one-line subhead, a link out to the source page.
- Time-range toggle: `1 year / 2 years / 5 years` — a global control that re-scopes every sparkline and every trend colour at once, not per-tile.
- Search box: client-side filter over indicator labels.
- Category filter chips: `All / Crime / Economy / Government / Health / Housing / Immigration / Living standards / Other` — single-select, filters the tile grid.
- Below the filters: a two-line legend, "X getting better" / "Y getting worse" (green dot / red dot counts), a running tally across whatever's currently filtered.
- Tile grid: responsive, 4 columns on desktop collapsing at breakpoints. Each tile:
  - Label (e.g. "Inflation") with an info icon (tooltip = the `note` field: source + definition).
  - Current value, large, with its unit (`2.6%`, `£271.3k`).
  - A trend arrow + delta, colour-coded (`↓ -1%` in green, `↑ +2%` in red), scoped to whichever range toggle is active.
  - A sparkline (thin line chart, no axes, shaded fill at the trend-colour tail) spanning the selected range.
- No drill-down / detail view was visible in the screenshot — this looks like a flat, single-screen dashboard, not a multi-page app.

## 2. Data model (confirmed from Times' own pipeline)

Their R script outputs one JSON array, each element:

```json
{
  "position": 1,
  "label": "Inflation",
  "note": "Consumer prices index, change on previous 12 months (ONS)",
  "parent": "Economy",
  "colour": "red",
  "colour2": "red",
  "colour5": "green",
  "now": 2.3,
  "change": 0.5,
  "change2": -1.2,
  "change5": 1.8,
  "unit": "%",
  "data": [ { "2024-01-01": 3.2 }, { "2024-02-01": 3.1 }, { "2024-03-01": 2.8 } ]
}
```

Two output files, `sparklines-page.json` and `sparklines-slice.json`, currently written identically (page = full site, slice = an embeddable widget version, same schema).

Key modelling decisions worth copying:
- **`up` direction is a per-indicator config value**, not inferred (`good`/`bad`/`neutral`) — e.g. rising inflation is bad, rising GDP is good, rising "flights" is neutral. This has to be a static property of each indicator definition, not derived from the data.
- **Colour is precomputed per range** (`colour`, `colour2`, `colour5`) rather than computed client-side from `change`/`change2`/`change5` — keeps the frontend dumb.
- **Missing data is forward-filled** (`zoo::na.locf()` — carry the last known value forward) so a sparse quarterly/annual series still draws a continuous line and the 1/2/5-year comparison always has a value to diff against, even if the exact date doesn't exist in the source.
- Category (`parent`) is a fixed enum matching the UI's filter chips.

## 3. Backend assumption — the important one

**There is no live backend API.** The Times' entire "backend" is a scheduled R script that pulls from ~15 government/market sources, computes the JSON above, and overwrites two static JSON files that the frontend fetches directly. No database, no ORM, no request-time computation. Freshness = however often the script is re-run (implied daily or on each data release, not continuous).

This matters for Phase 2: a from-scratch Python system doesn't need to serve a live query API to hit feature parity with the original. A SQLite-backed store is genuinely *more* capability than the source has, useful for history/debugging, but the public-facing artifact can still just be a generated JSON snapshot.

## 4. Swiss indicator mapping

23 of Times' 48 indicators skipped as UK-only novelties with no reasonable Swiss framing attempted here (e.g. "England world ranking" — no Swiss equivalent category). Remaining 25 core indicators mapped below; DIRECT = clean 1:1 source exists, ADAPTED = source exists but needs a proxy/different definition, UNMAPPABLE = no reasonable Swiss data exists.

### Economy & Living Standards & Government (research: Sonnet agent)

| Indicator | Feasibility | Swiss source |
|---|---|---|
| Inflation (CPI) | DIRECT | BFS LIK, STAT-TAB PxWeb API |
| Real GDP per capita | DIRECT | BFS/SECO national accounts |
| Unemployment rate | DIRECT | SECO (registered) / BFS SAKE (ILO definition) |
| Payrolled employees | DIRECT | BFS BESTA/STATEM, PxWeb API |
| Job vacancies | DIRECT | BFS job vacancy statistics, PxWeb API |
| NEETs 16-24 | ADAPTED | BFS SAKE NEET rate uses 15-29, not 16-24 |
| Redundancies | ADAPTED | No Swiss "redundancy" series; use SECO Kurzarbeit (short-time work) as leading proxy |
| Quarterly GDP growth | DIRECT | SECO Quarterly National Accounts |
| Debt-to-GDP ratio | DIRECT | BFS/EFV public finance; clarify gross vs net federal basis |
| Vehicle production | UNMAPPABLE → ADAPTED | Switzerland has no domestic production; substitute new vehicle registrations |
| Flight activity | ADAPTED | No single national feed; combine Zurich + Geneva airport monthly traffic |
| Debit card spend | ADAPTED | SNB payment statistics cube (less granular than Times' bank-partnership feed) |
| Petrol / diesel price | DIRECT | energiedashboard.admin.ch weekly fuel price series |
| Electricity price | DIRECT | ElCom Strompreis-Monitor (annual tariff-setting) |
| Cost of coffee/beer/meal | ADAPTED | No official published series either country; Numbeo-style crowdsourced pricing needed |
| Real wages | DIRECT | BFS Swiss Wage Index, PxWeb API |
| Real disposable income | DIRECT | BFS national accounts, annual only (no quarterly series) |
| SNB policy rate | DIRECT | data.snb.ch |
| Direct debit failure rate | UNMAPPABLE | UK-specific bank-partnership novelty, no Swiss source |
| 10Y government bond yield | DIRECT | data.snb.ch yield curve |
| National debt (CHF level) | DIRECT | EFV/BFS public finance |
| Renewables % of electricity | DIRECT | BFE electricity statistics |
| Net government approval | ADAPTED | No continuous tracker; only periodic SRG Trendbarometer/Sotomo polling around votes |

### Housing, Health, Crime, Immigration (research: Haiku agent)

| Indicator | Feasibility | Swiss source |
|---|---|---|
| House prices | DIRECT | BFS Swiss Residential Property Price Index (SWRPI), PxWeb API |
| House price-to-earnings | ADAPTED | No direct ratio; use price-to-rent as proxy |
| Housing starts/completions | DIRECT | BFS Buildings and Dwellings statistics, opendata.swiss |
| 2-bed rental cost | ADAPTED | BFS publishes average rent by canton/room count, not exactly "2-bed" |
| Rent as % of income | UNMAPPABLE | No official metric; would need manual BFS income + rent combination |
| Rough sleeping / homelessness | UNMAPPABLE | Only a one-off 2022 FHNW research study, not an ongoing series |
| Hospital waiting list size | UNMAPPABLE | Healthcare is cantonal, no national figure |
| Average wait duration | UNMAPPABLE | Cantonal |
| Seen within target time | UNMAPPABLE | Cantonal |
| A&E-equivalent 4hr | ADAPTED | opendata.swiss hospital key figures exist, but no wait-time KPI |
| Cancer treatment within target | UNMAPPABLE | Not centrally published |
| Bed occupancy rate | ADAPTED | opendata.swiss / WHO Euro gateway, cantonal aggregation only |
| Long-term sickness inactivity | ADAPTED | BFS Labour Force Survey cross-tab, not a standalone series |
| Survey-based crime estimate | ADAPTED | BFS PKS is police-reported only, no victimisation survey |
| Shoplifting offences | DIRECT | BFS PKS, PxWeb API |
| Theft from person | ADAPTED | Aggregated into general theft category in PKS |
| Knife/weapon crime | ADAPTED | Aggregated with other assault types in PKS |
| Prison population | DIRECT | BFS Imprisonment Statistics, monthly |
| Court caseload backlog | UNMAPPABLE | No unified national tracking, cantonal courts vary |
| Net migration | DIRECT | BFS population statistics / SEM |
| Asylum applications | DIRECT | SEM monthly statistics |
| Asylum grants/decisions | DIRECT | SEM monthly statistics |
| Small boat crossings | UNMAPPABLE | Switzerland is landlocked; no equivalent route exists at all |

### Net feasibility

Of 25 mapped indicators: **11 DIRECT, 10 ADAPTED, 6 UNMAPPABLE** (some indicators listed as both an UNMAPPABLE original and an ADAPTED substitute, e.g. vehicle production). Practical takeaway: a first version with ~20 solid indicators (all DIRECT + the stronger ADAPTED ones) is realistic without inventing data. The clean losses — small boat crossings, direct debit failures, rough sleeping as an ongoing series, a national hospital waiting list, a continuous government approval tracker — are structural (Switzerland is landlocked, has cantonal healthcare/justice, and consensus government), not a research gap. Don't force these; drop them or replace with the suggested proxies and say so in the UI copy (the `note` field is exactly the place for that honesty, matching the Times' own pattern of citing definitions).

## 5. Backend/API access patterns confirmed usable

- **BFS STAT-TAB / PxWeb API** — `https://www.pxweb.bfs.admin.ch/api/v1/[lang]`, POST JSON query, returns JSON-stat. This is the workhorse: covers CPI, wages, employment, vacancies, debt, house prices, PKS crime stats, population. One client function can serve most of the dashboard.
- **opendata.swiss** — CKAN API (`ckan.opendata.swiss/api/3/action/package_search`), aggregates datasets including some BFS/SEM/hospital ones as CSV/JSON.
- **SNB data portal** (data.snb.ch) — documented API, SDMX/CSV, for policy rate, bond yields, payment statistics.
- **SECO** — no public REST API; xlsx/CSV downloads from seco.admin.ch and amstat.ch. Will need a small scraper/parser, not a clean client.
- **SEM** (migration/asylum) — monthly PDF + some opendata.swiss datasets.
- **energiedashboard.admin.ch**, **ElCom**, **BFE** — each has its own CSV/chart export, no unified API.

## 6. Recommendation for indicator set v1

Pick ~15-20 DIRECT-feasibility indicators spanning at least 5 of the 7 categories for the first working pipeline (Phase 4), e.g.: CPI, unemployment, GDP growth, wages, house prices, petrol price, SNB policy rate, 10Y bond yield, national debt, PKS shoplifting, prison population, net migration, asylum applications, job vacancies, housing starts. That's enough category spread to prove the architecture without burning time on the ADAPTED/UNMAPPABLE cases up front.
