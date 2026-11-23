# Checks

## Verified from files (this session)
| Check | Result |
|---|---|
| Control totals: all 29 measures recomputed from the built tables, the way the DAX measures define them (`pipeline/build_star.py`) against the independent pandas figures (`pipeline/expected_numbers.py`) | 29 of 29 match |
| Row counts: Sales = 112,650 lines + 775 orders with no line = 113,425; Payments = 103,886 | match |
| Every fact key exists in its dimension, every dimension key is unique | asserted in `build_star.py` |
| `design_gate.py` | RESULT: GO |
| `pbip_check.py` | 0 errors, 0 warnings |
| pbip-validator agent, first run (model only; the data visuals did not exist yet) | no errors; its finding (missing `ref table` lines after a rerun) was a generator bug, fixed |
| pbip-validator agent, second run (structure, fields and roles only; it did NOT validate against the Microsoft JSON schemas and missed 3 schema errors, found later) | no errors, no warnings: TMDL tabs and names, ref lines, 12 relationships, 71 measures' references, 84 data visuals (fields, roles, 12 TopN filters, syncGroups, positions, no overlaps). Not run: pbir schema validation, the DAX engine, M |
| Every Entity/Property of the 84 data visuals (195 references) resolves to a model column or measure | all resolve (own script, plus `pbip_check.py`) |
| Measures not used by any visual, filter or other measure (dependency analysis) | 7 of 70, kept on purpose from the earlier report's measure list (not on a page): Average Installments, Average Payment, Average Payment per Order, Boleto Share %, Credit Card Share %, Review Share %, Share of Revenue % |
| DAX syntax of 15 of the trickiest measures (SQLBI DAX Formatter service) | valid |
| Reference match of the Overview background and the cover against the approved backgrounds (`reference_match.py`) | MATCH |
| `te validate` / Tabular Editor parse of the TMDL | not run: the `te` CLI is not installed here; the generator output was compared with the SpaceParts example for structure, nothing parsed it |
| Expected values for the comparison measures with Year = 2018 (`control-totals-2018.md`, pandas) | written; Desktop must confirm (second query in `verify-measures.dax`) |

## Not verified (needs Power BI Desktop; only Omar's screenshots verify rendering)
- That the model loads and refreshes (Power Query reads the CSVs in `data/`; no M engine here).
- That the 70 DAX measures return the control totals: run `powerbi/verify-measures.dax` once (DAX query view) and compare with `powerbi/control-totals.md`.
- How any page renders: the visuals, the top-N filters, the map, the default Year = 2018 selection on the slicers, the arrows of the comparison lines.
- The comparison lines are not coloured green or red: the format string carries the arrow and sign only. Colouring them needs a conditional-format rule per card in Desktop.

## Added 2026-11-23
| Check | Result |
|---|---|
| Every JSON against Microsoft's published schemas (visualContainer 2.13.0, page 2.1.0, report 3.3.0, pagesMetadata 1.1.0, version 1.0.0), tools in `olist-report-bisect	ools\` | found 3 error kinds (syncGroup at root, string sort field, `$schema` 2.14.0 does not exist); the first two and my 84 visuals' `$schema` are fixed; left: `$schema` constants on the 104 `ff_*` visuals and 9 pages from `make_frames.py` |
| Determinism: rerun of `build_model.py` and `build_pages.py`, hash of both definition folders | identical |
| 29 control totals after the 5 new measures | 29 of 29 (data unchanged) |

## Added 2026-11-23 (redesign)
| Check | Result |
|---|---|
| Reviews bug: `Reviewed Orders` replaced the score filter of the axis; expected per score with Year 2018 (pandas): 5,436 / 1,579 / 4,222 / 10,108 / 31,123 | fixed with KEEPFILTERS; values to be confirmed in Desktop |
| Pandas chart numbers for other pages | `08-chart-numbers.md` |
| Bar and column charts per page | at most 2 (script count) |
| `pbip_check.py` | 0 errors, 4 deliberate warnings (waterfall, 2 pies, gauge) |
| Determinism after the redesign (model, pages, post_frames rerun) | identical hashes |
| Not verified: rendering of every new visual type, colour measures, treemap/pie/gauge/waterfall properties, trend lines, the nav label fix, the card chrome fix | Desktop |

## Round 3 (2026-11-23, from Omar's screenshots)
Verified from files: schema 0 errors on my 84 visuals, determinism identical, DAX syntax of the colour measures. Not verified (Desktop): comparison lines and their colours, card border gone, label size 9 pt, bars without scrollbars, nav label spacing, the refreshed delivery status text.
