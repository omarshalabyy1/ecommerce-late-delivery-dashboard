# Handover: Olist report rebuild (2026-11-22)

## State
`olist-report/` holds a new Power BI project built stage by stage with the powerbi-kit hub (plugin 0.1.15, scripts from 0.1.16): S0 to S13 done. The old build was moved, not deleted, to `olist-report-old/`.
Verified from files: 29 of 29 control totals match in pandas on the built tables, `design_gate.py` GO, `pbip_check.py` 0 errors 0 warnings, pbip-validator agent clean on the finished files. Not verified: Power BI Desktop load and refresh, the DAX values, how any page renders (only Omar's Desktop run and screenshots can show that).

## Files touched (all inside `olist-report/` unless noted)
- `olist_e_commerce_report.pbip`, `.SemanticModel/definition/*` (TMDL: 10 tables plus `_Measures`, 12 relationships, 70 measures, parameter `Data Folder`), `.Report/definition/*` (cover + 8 pages, 9 drawn backgrounds, 84 data visuals, theme `OlistTheme.json`).
- `pipeline/`: `build_star.py` (nine CSVs to `data/*.csv`, asserts keys and the 29 totals, writes `powerbi/control-totals-2018.md`), `build_model.py`, `measures.py`, `build_pages.py`, `expected_numbers.py`.
- `powerbi/`: `state.md`, `01-brief.md`, `02-pages.md`, `03-design-brief.md`, `04-model.md`, `05-checks.md`, `README.md`, `spec.json`, `layout.json`, `theme.json`, `brand/`, `backgrounds/`, `control-totals.md`, `control-totals-2018.md`, `verify-measures.dax`.
- `data/` (generated CSVs, about 45 MB) and `.pbi` caches are not git-ignored; nothing is committed.

## Open items, in order
1. Omar opens the PBIP in Desktop, sets the `Data Folder` parameter if the path differs, refreshes.
2. Run both queries in `powerbi/verify-measures.dax`; compare with `control-totals.md` and `control-totals-2018.md`.
3. Omar sends a screenshot of every page and the model view; fix from them. First things to look at: KPI strip width (cards are about 76 px wide for label, value and comparison), Year slicer opening on 2018, the map, the top-N bars.
4. Add a `.gitignore` for `data/` and `.pbi/` before any commit.

## Gotchas
- The CSVs live at `D:\Learning\Courses\Other\Instant Software Solution\grad`, not in the repo; `python pipeline/build_star.py "<folder>"` rebuilds `data/`.
- The facts never relate to each other; order-level values (review, delivery days) repeat on each order line, so measures count distinct orders. Order-level measures by category or seller do not add up to the total.
- `Revenue vs LY` for 2017 compares with a 2016 that starts in September; 2016 comparisons are blank. Comparison lines carry arrows, not green or red colour.
- Card and chart formatting property names and the top-N filter shape were written from templates, not confirmed by Desktop.
- The `te` CLI is not installed, so no Tabular Editor parse of the TMDL ran.
- Rerunning `build_model.py` or `build_pages.py` regenerates their files; `make_frames.py` owns the `ff_*` frame visuals and backgrounds.

## Update 2026-11-23
- Omar's Desktop: the cover renders and the model loads; pressing Refresh now blanked the canvas with "Failed to load the report". Static diagnosis in `olist-report/powerbi/07-load-failure.md`: schema validation found `syncGroup` at the root of 16 slicers, string sort fields in 3 tables and a non-existent `visualContainer/2.14.0` `$schema`. The first two and the `$schema` of my 84 visuals are fixed at source in `pipeline/build_pages.py`; the 104 `ff_*` frame visuals and 9 pages from `make_frames.py` still carry 2.14.0 and `page/2.0.0`. Whether the project now loads is untested.
- Bisect copies b1 to b5 in `olist-report-bisect/` (made before those fixes; b5 is the schema-clean variant).
- Tricks pass applied (`powerbi/06-tricks-plan.md`, status table at the end): 5 new measures (75 in total), slicer labels and single-select Year, legend and last-year colours, rank helpers with a 200-order floor, table grid, Revenue in millions. Rows 4, 9, 10, 13 skipped.
- Open items: Omar's result on the bisect copies and on the real project; ask the parent session to set `make_frames.py` to visualContainer 2.13.0 / page 2.1.0; `.gitignore` for `data/`, `.pbi/` and `olist-report-bisect/`.

## Update 2026-11-23 (visual and analytical redesign)
Wave 1: KPI card chrome off, labels off on two-series charts, new `Revenue Growth %` card value, Delivery Status "No date", map lat/long as hidden average measures, nav labels 9 pt (`pipeline/post_frames.py`, run after `make_frames.py`), the Reviews score chart bug (CALCULATE filter on the axis column replaced the score; fixed with KEEPFILTERS), table column widths, `Month Start` date axis and monotone smoothing. Wave 2: treemaps, combo, waterfall, stacked area, pies, scatter, gauge, leader highlight colours, trend lines; plan and status in `olist-report/powerbi/09-wave2-plan.md`. Waiting on Omar's Desktop samples for measure-bound reference lines, table heat, small multiples, filled/Azure map and Analytics-pane lines; 92 measures now.

## Update 2026-11-23 (round 3, from screenshots)
Omar's screenshots showed the new charts rendering. Fixed: comparison lines did not render (now the reference-label Detail structure from `card-kpi-with-yoy.md`, with hidden colour measures `... vs LY CF`), card border (base theme `borderCustom`/`outline` need selector id default), label size, chart subtitles, vertical gridlines, trend-line clutter on Overview, scrollbars on bar charts (5 to 7 members), Sellers scatter limited to the top 100 by revenue. Open: Omar must refresh the model so Delivery Status shows `No date`; 115 measures.

## Round 4 (2026-11-23)
KPI card height given back (layout padding removed, 84 px of the 88 px slot) so the comparison line can show; rate lines straight; Products and Sellers top charts show 5 bars. Verified from files: gate GO, pbip_check 0 errors / 4 deliberate warnings, determinism identical. Desktop: comparison lines.

## Update 2026-11-23 (repo front page)
README.md rewritten around the new report and a pain-first name ("Marketplace delivery dashboard": what late deliveries cost in reviews, which sellers and states cause it); every number in it re-measured from the built tables (late 6.8%, 2.27 vs 4.29 stars, 54% vs 7% one-star, top 10% of sellers 67.1%, top 10 categories 62.4%, repeat 3.0%, 2018 +145.1%). Header SVG text updated, screenshots in `docs/screenshots/` (taken before the last KPI comparison-line fix: retake), `.gitignore` covers `olist-report/data/`, `.pbi/`, the bisect and old copies. Not committed. Suggested GitHub repo name: `marketplace-delivery-dashboard` (now `olist-power-bi-report`).
