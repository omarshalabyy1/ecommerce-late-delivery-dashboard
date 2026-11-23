# Olist marketplace report: hand-over

Nine pages on the Olist Brazilian e-commerce data (orders Sep 2016 to Oct 2018): a cover, seven pages that each answer one question, and a data table. Layout: top navigation bar, KPI strip, four visuals per page.

## Open it
1. `python pipeline/build_star.py "<folder with the nine Olist CSV files>"` writes the model tables to `data/` and checks the 29 control totals. (Already run once.)
2. Open `olist_e_commerce_report.pbip` in Power BI Desktop.
3. If the `Data Folder` parameter does not point at `olist-report\data` on your machine: Transform data, Manage parameters, `Data Folder`.
4. Refresh. Then run `powerbi/verify-measures.dax` (DAX query view) and compare with `powerbi/control-totals.md`.

## Pages
| Page | Question | Background | Visuals (measures) |
|---|---|---|---|
| Cover | What is this and where do I start? | `bg_pg00Cover.png` | 8 navigation tiles |
| Overview | How is the business doing? | `bg_pg01Overview.png` | Revenue, Orders, Average Order Value, Customers, Average Review with `vs LY`; revenue by month with last year; payment share by type; top 5 categories; top 8 states by orders |
| Sales | Are we growing against last year? | `bg_pg02Sales.png` | Revenue vs LY %, Items Sold, Average Item Price, Freight % of Revenue, Revenue per Customer; revenue by month per year; by weekday; top 10 states; by region |
| Products | What sells? | `bg_pg03Products.png` | Revenue, Items Sold, Categories With Sales, Average Item Price, Top Category Share; top 10 categories; revenue trend; price bands; category table |
| Customers | Who buys, and do they come back? | `bg_pg04Customers.png` | Customers, New Customers, Repeat Customers %, Orders per Customer, Revenue per Customer; new and returning orders by month; map of the 500 largest cities; top 10 states and cities |
| Delivery | Do orders arrive when promised? | `bg_pg05Delivery.png` | Late Deliveries %, Average Delivery Days, Average Days Late, Late Orders, Cancellation %; late % by month; on time against late; slowest and latest states |
| Reviews | How do customers rate us? | `bg_pg06Reviews.png` | Average Review, One Star %, Five Star %, Review Rate %, Average Review Late; score distribution; score by month; 10 lowest categories; on time against late |
| Sellers | Who sells, and who delivers late? | `bg_pg07Sellers.png` | Active Sellers, Revenue per Seller, Late Deliveries %, Average Review, Freight % of Revenue; top 10 sellers; sellers by state; late % against review per seller; seller table |
| Data table | Can I take the numbers to Excel? | `bg_pg08DataTable.png` | month x state table with a Total row |

Slicers on every analysis page: Year (set to 2018 on open) and State, synced across pages. The `vs LY` lines compare the selected year with the same days of the year before, up to the last sale date; they are blank unless exactly one year is selected. Page navigation: the ff_nav* buttons.

## To change X, edit Y
| Change | Edit |
|---|---|
| A measure | `pipeline/measures.py`, then `python pipeline/build_model.py` (or edit the measure in Desktop; the table is `_Measures`, folders Sales, Growth, Customers, Delivery, Reviews, Payments, Sellers, Comparisons) |
| A table or column | `pipeline/build_star.py`, then `pipeline/build_model.py` |
| Which visuals sit on a page | `pipeline/build_pages.py`, then rerun it (it only replaces visuals named kpi*, chart*, slicer*) |
| Colours | `powerbi/theme.json` (made from `powerbi/brand/brand.json`), copy to `Report/StaticResources/RegisteredResources/OlistTheme.json`; frames: `python make_frames.py` with `powerbi/spec.json` |
| Page frames, navigation, icons, cover | `powerbi/spec.json`, then `make_frames.py` from the powerbi-kit hub (writes backgrounds, ff_* visuals, `powerbi/layout.json`) |
| The data folder | the `Data Folder` parameter |

## Brand choices
- Palette taken from the Olist logo (olist.com): blue `#0A4EE4` as the one accent, the logo's orange-red dot `#E14E3A` as second data colour, near-black navy `#111B33` as the darkest surface, page `#F4F6F8`, white rounded cards.
- Layout (top navigation, KPI strip) was picked by the hub's hash of the client name, so it differs from the Accounts Receivable report.
- 3D Fluent icons from the kit on the navigation, KPI tiles and cover tiles; real visuals only on the canvas, the frame is the background image.
- Good and bad colours (`#2E9E6B`, `#C2410C`) are reserved for meaning; the comparison lines use arrows and signs.
- Every KPI has a comparison (last year, or the leader or gap where last year makes no sense).

## Known limits
- Order-level measures on a category or seller axis count an order under every category or seller it touches, so those rows do not add up to the total.
- Revenue vs LY for 2017 compares with 2016, which starts in September: the growth is real but inflated. 2016 has no earlier year, so its comparisons are blank.
- Comparison lines are not coloured green or red (arrow and sign only); the delivery states top 10 by late % includes small states.
- Nothing here has been opened in Desktop yet: see `05-checks.md` for what is and is not verified.
