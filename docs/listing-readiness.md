# Listing readiness

Audit of 2026-11-22: is this dashboard ready to be the proof piece behind a "Power BI dashboard from your Excel, CSV or SQL data" listing?

## Verdict: PARTIAL

The build is complete and every number in the README and in Omar's profile reproduces from the data. Three things are missing before it can go into a listing, and only Omar can do them: a fresh check in Power BI Desktop (the model changed after the last one), one screenshot to retake, and a decision on the unfinished `olist-report/` folder. The list is at the end.

## What was measured

Every number below was computed by script, not copied from the README. Two independent routes gave the same result:

1. A new pandas script read the seven Olist CSV files directly (the files are outside this repo, in the graduation-project folder) and applied the repo's rules: a sale is an item of a delivered order, late means delivered after the estimated date (dates only), each order keeps its latest review.
2. The notebook `analysis/analysis.ipynb` was run on a clean copy of the repo with those files. It finished without error, so its own pandas-against-SQL assertions passed. The report that `powerbi/build_pbip.py` wrote from that run is byte-identical to the committed `powerbi/sales-performance.Report/` and `.SemanticModel/`, except the output-folder path and the random relationship ids. The three README charts in `docs/` also came out byte-identical.

| Claim | Where it is made | Measured |
|---|---|---|
| 96,478 orders | README, profile | 96,478 delivered orders |
| Revenue 13,221,498 | README, check C6 | 13,221,498.11 from 110,197 items |
| Customers 93,358; repeat buyers 3.0% | README, C8, C9 | 93,358; 3.00% |
| Late orders 2.27 stars against 4.29 on time | README, profile | 2.27 and 4.29 (all orders 4.16) |
| 54% and 7% one-star, late against on time | README, C37 | 53.8% and 6.6% |
| Late deliveries 6.8% | README, C10 | 6.77% (6,534 orders) |
| Top 10% of sellers bring 67% of revenue | README, profile | 297 of 2,970 sellers bring 67.11% |
| 2018 up 145.1% on the same days of 2017 | README, C17 | 7,218,125.12 against 2,944,431.50, +145.1% |
| Top 10 of 74 categories bring 62.4% | README, C26 | 74 categories, 62.4% |
| Late deliveries highest in AL, 21.4% | README, C38 | AL, 21.4% |
| Row-level security per region | README, profile, C39 to C43 | five roles in `model.bim`, each filtering `dim_seller[seller_region]`; revenue by seller region is 10,354,931.00, 2,219,100.72, 455,082.78, 185,206.41 and 7,177.20, which add up to the total with no seller left without a region |
| Table sizes C1 to C5 | `powerbi/06-checks.md` | 110,197; 1,096 days; 32,951; 3,095; 99,441 |

What the scripts cannot show: that the DAX measures return these values inside Power BI Desktop. `powerbi/README.md` says all 43 checks were run in Desktop on 2026-10-05. Commit `25f51b7` (2026-10-09) changed the `dim_date` range after that, so the Desktop check is older than the model.

## Files

| Item | State |
|---|---|
| `powerbi/sales-performance.pbip` | 5 pages, 56 visuals, 23 measures, 4 relationships, 5 security roles. Valid JSON in all 67 report files. It is a Power BI project, not a `.pbix`. `pbip_check.py` could not audit it: it needs TMDL and this model is `model.bim`. |
| Gallery screenshots | `powerbi/screenshots/01-overview.png` to `05-delivery.png`, about 1308 x 730. They show the right numbers. `05-delivery.png` has a selected-visual frame and hover toolbar on the review-scores chart. `04-sellers.png` has a table that fills only half its box. |
| Refresh guide | Was missing and was wrong: `powerbi/README.md` said to open the file and click Refresh, but the committed `OutputFolder` is a placeholder (`C:\Users\you\...`) and `output/` does not exist in a fresh clone. |
| `olist-report/` | A separate ten-page, 46-measure report on all nine Olist files. Its `checks.md` reproduces exactly from `expected_numbers.py`, and the order count and the two review averages from the profile match. It has no security roles, `DataFolder` points to `D:\Learning\...`, and its README says it is not yet confirmed in Desktop. It does not back any claim in the profile. |

## What I changed

1. `powerbi/README.md`: "The fast way" now has the one-line refresh guide and the missing `OutputFolder` step.
2. `output/` (ignored by git): the five tables the notebook writes, taken from the clean-copy run, so the report can be refreshed on this machine at once.
3. This file.

Only `powerbi/README.md` and this file were committed. `olist-report/` and the uncommitted one-line path edit in `powerbi/01-power-query.md` (its example path says `ecommerce-late-delivery-dashboard`, the GitHub repo name since 2026-11-23) were left as found.

## Omar must do by hand

1. Open `powerbi/sales-performance.pbip` in Power BI Desktop. Under Transform data, Edit parameters, set `OutputFolder` to `C:\Users\DELL\GitHub\sales-performance-dashboard\output\` (with the final backslash) and refresh. Compare the cards with `powerbi/06-checks.md` C6 to C38, then use Modeling, View as for the five roles and compare C39 to C43. This is the check the listing rule in `powerbi-kit\gigs\README.md` asks for, and it is newer than the model change of 2026-10-09.
2. Retake `powerbi/screenshots/05-delivery.png` with no visual selected (click an empty part of the canvas first). Optionally widen the table in `powerbi/screenshots/04-sellers.png`.
3. Pick the gallery from the five files. Suggested order, cover first: `01-overview.png`, `02-sales.png`, `04-sellers.png`, `05-delivery.png`. `gigs\README.md` has no listing or file names for this dashboard, so these names are used as they are. The images show Brazilian states and BRL but not the word Olist; check each platform's rules before uploading.
4. Decide about `olist-report/`: open it in Desktop and verify it before using it anywhere, or leave it out of every listing. Also commit or revert the edit in `powerbi/01-power-query.md`.
5. In `client-radar\profile.md` the project link is `github.com/omarshalabyy1/sales-performance-dashboard`; the repo was renamed to `ecommerce-late-delivery-dashboard`. GitHub redirects the old name, but update the link when convenient. That file is outside this repo and was not touched.
