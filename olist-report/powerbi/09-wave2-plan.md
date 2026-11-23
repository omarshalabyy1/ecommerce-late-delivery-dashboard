# Wave 2 plan: charts with meaning, analytics pane, colour that encodes something (2026-11-23)

Rules kept: one question per page, titles that ask the question, 1280 x 720 grid, 249 x 88 KPI slots, arrows beside colour. At most 2 bar or column charts per page (stacked and combo columns count). Colours only from look.md and `brand.json`: accent `#0A4EE4`, second `#E14E3A`, good `#2E9E6B`, bad `#C2410C`, neutral `#8A94A0`, dark `#111B33`, soft `#E6EDFF`, LY grey `#C9D3DC`, quiet blue `#91B4FF` (data colour 3 of the theme). **No new colour tokens are needed**; nothing to approve.

## Colour rules used
- **Leader highlight**: the top item in the accent, the rest in quiet blue `#91B4FF`. A hidden measure returns the hex (`... Leader Colour`).
- **Good / bad**: on time green, late red; scores 1 to 2 red, 3 grey, 4 to 5 green; states worse than the overall average red, others grey. Lower-is-better is inverted by the measure, not by the chart.
- **Categorical** only for 2 to 5 members with a fixed meaning: payment types, new vs returning, on time vs late, repeat vs one-time.
- **Region** colours come from the theme data colours (5 regions = 5 theme colours).

## Property sources (what is confirmed in a file I hold)
| Feature | Source | Confidence |
|---|---|---|
| Visual types and query roles (`treemap` Group/Details/Values, `pieChart`, `areaChart`/`stackedAreaChart`, `lineClusteredColumnComboChart` ColumnY/LineY, `waterfallChart` Category/Y, `gauge` Y/MinValue/MaxValue/TargetValue, `scatterChart`, `map`) | `pbir-report-builder/references/visual-types.md`, `pbir-format` examples | high |
| Series colour by measure: `dataPoint.fill` with `selector.metadata` | `lineChart.json` example | high |
| Colour per category: `dataPoint.fill` with `selector.data[].scopeId.Comparison` | `donutChart.json` example | high |
| Colour from a measure (hex text): `dataPoint.fill` = Measure expr, selector `dataViewWildcard matchingOption 1` | `scatterChart.json` example | high |
| Waterfall colours `sentimentColors` increaseFill, decreaseFill, totalFill | `waterfallChart.json` example | high |
| Constant / reference line `y1AxisReferenceLine` show, value, lineColor, style, dataLabelShow; `xAxisReferenceLine` | `pbir-format/references/visual-json.md` | high for the structure; **medium** that `value` accepts a measure expression (the trick text says "fx = measure", no JSON example) |
| Trend line `trend` show, lineColor, transparency, style | same file | high |
| Forecast `forecast` show, forecastLength, confidenceBandStyle, confidenceLevel | same file | high structure; not used (see rows) |
| Error bars `error` (barColor, barWidth, selector metadata); measure bounds `errorRange.explicit` | same file | structure only, bounds not shown: not used |
| Average, min, max, median, percentile lines of the Analytics pane; anomaly detection (`anomalyDetection` listed, no properties); symmetry shading | no file | **unknown: sample needed** |
| Matrix / table cell heat `values.backColor` with `FillRule` gradient | `tableEx-gradient.json` shows `fontColor` with FillRule | medium (backColor name assumed from the same pattern) |
| Small multiples `smallMultiplesLayout` | listed in examples, no property list | unknown: sample needed |
| Filled map / shape map / Azure map | roles listed, no example, Brazil geography unconfirmed | unknown: sample needed |

## One row per chart
| Page | Chart | Now | New visual | Field roles | Colour | Analytics | Why / confidence |
|---|---|---|---|---|---|---|---|
| Overview | 1 | line, Revenue + Revenue LY | line (kept) | Category `Month Start`; Y Revenue, Revenue LY | Revenue accent, LY grey dashed (done) | trend line on the visual, neutral dashed, transparency 20. No forecast: the data ends 29 Aug 2018 and Nov 2017 is a one-off peak, a forecast would mislead | trend: high |
| Overview | 2 | bar, payment share | **treemap** | Group Payment Type; Values Payment Value | credit card accent, boleto `#E14E3A`, voucher `#91B4FF`, debit `#5B6B7A`, not defined `#C9D3DC` (scopeId) | none | share of a whole with 5 members; no centre text to cut. high |
| Overview | 3 | bar, top 5 categories | bar (kept) | Category Product[Category]; Y Revenue; Top N 5 | leader accent, rest quiet blue (`Category Leader Colour`) | none | 1 of 2 bars. high |
| Overview | 4 | bar, orders by state | bar (kept) | Category State; Y Orders; Top N 8 | leader accent, rest quiet (`State Orders Leader Colour`) | none | 2 of 2 bars. high |
| Sales | 1 | clustered columns, this vs last year | **combo** (columns + line) | Category `Month`; ColumnY Revenue; LineY Revenue LY | columns accent, LY line grey | reference line = `Revenue Monthly Average` (new measure), neutral dashed, label on | 1 column chart. line: medium |
| Sales | 2 | columns, weekday | columns (kept) | Category Weekday; Y Revenue | best weekday accent, others quiet (`Weekday Leader Colour`) | none | 2 columns. high |
| Sales | 3 | bar, top 10 states | **treemap** | Group Region; Details State; Values Revenue | region colours from the theme | none | composition by region and state in one view. high |
| Sales | 4 | bar, region | **waterfall** | Category Region; Y `Revenue Change vs LY` (new measure) | increase good, decrease bad, total accent (sentimentColors) | none | which regions drive the growth against last year. high |
| Products | 1 | bar, top 10 categories | bar (kept) | Category Category; Y Revenue; Top N 10 | leader accent, rest quiet | none | 1 bar. high |
| Products | 2 | line, revenue by month | line (kept) | Category `Month Start`; Y Revenue | accent | trend line (neutral dashed) | analytics pane use. high |
| Products | 3 | columns, price band | columns (kept) | Category Price Band; Y Items Sold | best band accent, rest quiet (`Price Band Leader Colour`) | none | 2 columns. high |
| Products | 4 | table | table (kept) | Category, Revenue, Items Sold, Average Item Price, Average Review | Average Review cell heat: bad `#C2410C` to white to good `#2E9E6B` | none | heat via `backColor` FillRule: medium |
| Customers | 1 | stacked columns, new vs returning | **stacked area** | Category `Month Start`; Y New Orders, Returning Orders | New accent, Returning `#E14E3A` (metadata) | none | composition over time, no columns. high |
| Customers | 2 | map (city bubbles) | map (kept; aggregates fixed in wave 1) | Category City; X City Longitude; Y City Latitude; Size Customers | quiet blue bubbles | none | Bing map shows a "going away" notice; a filled or Azure map needs a sample (Brazil geography). high for the kept map |
| Customers | 3 | bar, top 10 states | **pie** (2 slices) | Category Customer Type; Y Customers | repeat accent, one-time `#C9D3DC` (scopeId) | none | answers "do they come back?" directly; a pie has no centre text. high |
| Customers | 4 | bar, top 10 cities | bar (kept) | Category City; Y Customers; Top N 10 | leader accent, rest quiet (`City Leader Colour`) | none | 1 bar. high |
| Delivery | 1 | line, late % by month | line (kept) | Category `Month Start`; Y Late Deliveries % | bad `#C2410C` (late is bad) | reference line = `Late Deliveries % Overall`, neutral dashed, label on | line: medium |
| Delivery | 2 | donut (centre text cut) | **pie** | Category Delivery Status; Y Orders | on time good, late bad, no date neutral (scopeId) | none | removes the cut centre text. high |
| Delivery | 3 | bar, slowest states | **scatter** | Category State; X Average Delivery Days; Y Late Deliveries %; Size Delivered Orders | states above both overall averages bad, others neutral (`State Delivery Colour`) | reference lines on both axes = `Average Delivery Days Overall`, `Late Deliveries % Overall` | shows speed against reliability, size shows volume. high / lines medium |
| Delivery | 4 | bar, late states | bar (kept) | Category State; Y Late Deliveries %; Top N 10 on `Late Rank Helper` | above the overall average bad, else neutral (`Late State Colour`) | none | 1 bar. high |
| Reviews | 1 | columns, score counts | columns (kept) | Category Review Score; Y Reviewed Orders | scores 1 to 2 bad, 3 neutral, 4 to 5 good (`Score Class Colour`) | none | 1 column chart. high |
| Reviews | 2 | line, average review by month | line (kept) | Category `Month Start`; Y Average Review | accent | reference line = `Average Review Overall`, trend line | line: medium, trend: high |
| Reviews | 3 | bar, lowest categories | bar (kept) | Category Category; Y Average Review; bottom 10 on `Review Rank Helper` | bad `#C2410C` (they are the lowest) | none | 2 of 2 with Reviews 1. high |
| Reviews | 4 | columns, on time vs late | **gauge** | Y Average Review Late; MinValue `Score Scale Min`; MaxValue `Score Scale Max`; TargetValue Average Review On Time | value bad, target neutral | target marker = on-time score | the gap is the answer; two new hidden constant measures. high |
| Sellers | 1 | bar, top 10 sellers | bar (kept) | Category Seller; Y Revenue; Top N 10 | leader accent, rest quiet (`Seller Leader Colour`) | none | 1 bar. high |
| Sellers | 2 | bar, sellers by state | **treemap** | Group Seller State; Values Active Sellers | accent (single measure, one colour) | none | share of sellers by state. high |
| Sellers | 3 | scatter | scatter (kept) | Category Seller; X Late Deliveries %; Y Average Review; Size Revenue | sellers worse than average on both bad, others quiet (`Seller Risk Colour`) | reference lines at `Late Deliveries % Overall` and `Average Review Overall` | outlier marking by colour; true anomaly detection needs a sample. high / lines medium |
| Sellers | 4 | table | table (kept) | Seller, State, Revenue, Orders, Late %, Review | Average Review heat as Products 4 | none | medium |
| Data table | 1 | table | table (kept) | as before | none | none | export page, stays plain |

## New measures (all hidden unless noted; hex text or numbers; DAX syntax checked with DaxFormatter)
`Category Leader Colour`, `State Orders Leader Colour`, `Weekday Leader Colour`, `Price Band Leader Colour`, `City Leader Colour`, `Seller Leader Colour` (rank 1 on the axis field, accent else `#91B4FF`); `Late State Colour`, `State Delivery Colour`, `Seller Risk Colour` (above overall average = bad, else neutral); `Score Class Colour`; `Revenue Monthly Average`, `Late Deliveries % Overall`, `Average Delivery Days Overall`, `Average Review Overall` (`CALCULATE ( [X], ALLSELECTED () )`); `Revenue Change vs LY` (visible, Growth folder); `Score Scale Min`, `Score Scale Max`.

## Needs a Desktop sample from Omar (nothing built on a guess)
1. **Analytics pane lines**: on any line chart add an Average line, a Min line, a Max line, a Median line and a Percentile line (95), and an Anomaly detection; save. I copy the exact JSON (these have no `value` and no example in my files).
2. **Small multiples**: one bar or line chart with the Small multiples well filled, save.
3. **Filled map and Azure map**: one of each for Brazilian states or cities (field set-up, map type), save; I then replace the Bing `map` on Customers.
4. **Matrix or table heat**: one table with Background colour > Gradient on a measure, save, to confirm `backColor`.
5. **Reference line bound to a measure**: one constant line whose value is a measure (fx), save, to confirm the `value` expression.
Anything not confirmed from files is built with the structure above or left out; see the delivered list.

## Built (2026-11-23) and not built
Built from the table above (all through `build_pages.py`, 92 measures in `measures.py`): Overview treemap for payments with fixed member colours; Sales combo (columns + dashed LY line), treemap by region and state, waterfall of the change vs LY with good/bad/accent; Customers stacked area (new accent, returning `#E14E3A`), pie repeat vs one-time; Delivery pie on time green / late red / no date grey, scatter (delivery days against late %, size delivered orders, red when worse than overall on both); Reviews gauge (late average, on-time average as target, scale 1 to 5), score columns coloured by class, bottom-10 bars in bad; Sellers treemap by state, scatter with the risk colour; leader highlight (accent against quiet blue) on every kept bar and column chart; trend lines (documented JSON) on Overview revenue, Products revenue, Reviews average review. Bar and column charts per page: Overview 2, Sales 2, Products 2, Customers 1, Delivery 1, Reviews 2, Sellers 1.

**Not built, waiting for the Desktop samples listed above:** reference lines bound to a measure (Sales combo average, Delivery late % average, Reviews average, scatter average lines), table heat on Average Review, small multiples, filled / Azure map (the Bing `map` stays), Analytics-pane average, min, max, median, percentile lines and anomaly detection, error bars. No forecast, on purpose.

**Checker note:** `pbip_check.py` prints 4 warnings, "waterfallChart / pieChart / pieChart / gauge on the page (look.md section 8)". They are deliberate (Omar asked for other chart types); the pies have 2 and 3 slices. `design_gate.py` is GO.
