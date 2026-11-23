# Page plan: one business question per page

> **As built (2026-11-22):** the plan below holds, with these changes. Top navigation instead of the sidebar; every KPI has a `... vs LY` comparison measure or a leader/gap line; the Overview payment donut is a bar chart (5 types); the Sales page compares Revenue with Revenue LY by month (the Year slicer opens on 2018); the Data table page has 4 KPIs.

Page size 1920 x 1080 is not assumed: size is read from the saved PBIP at S5 (look.md §1). Every analysis page: 200 px dark sidebar (logo, page buttons), header with title, question subtitle and slicers (Year, State), a KPI row of 4 or 5 cards, about 4 main visuals. Comparison for every KPI: "vs last year" (same days) unless stated.

| # | Page | Question | KPIs (formula, comparison) | Main visuals |
|---|---|---|---|---|
| 0 | Cover | What is this and where do I start? | none | Title, purpose line, one navigation tile per page |
| 1 | Overview | How is the business doing? | Revenue (sum of item price, delivered orders; vs LY); Orders (delivered orders; vs LY); Average Order Value (Revenue / Orders; vs LY); Customers (distinct customer_unique_id; vs LY); Average Review (mean latest score; vs LY) | Revenue by month (smooth line, previous year dashed); revenue by category group (top 5 bars); payment type share (donut, 3 slices: credit card, boleto, other); orders by state (bars) |
| 2 | Sales | Are we growing against last year, and where? | Revenue vs LY % (growth); Items Sold; Average Item Price; Freight % of Revenue; Revenue per Customer (all vs LY) | Revenue by month this year vs last (columns); revenue by weekday (columns, peak accent); revenue by state (top 10 bars); revenue by region (donut) |
| 3 | Products | What sells? | Revenue; Items Sold; Categories With Sales (count); Average Item Price; Share of Revenue of the top category | Top 10 categories by revenue (bars); revenue trend of the top category (line); price band vs items (columns); category table (revenue, items, avg price, avg review) |
| 4 | Customers | Who buys, and do they come back? | Customers; New Customers; Repeat Customers % (customers with a second delivered order / customers); Orders per Customer; Revenue per Customer | Customers by state (bars); new vs returning orders by month (columns); customer map by zip prefix (map, bubble = customers); top 10 cities (bars) |
| 5 | Delivery | Do orders arrive when promised? | Late Deliveries % (late / delivered with date); Average Delivery Days; Average Days Late (late orders only); Late Orders; Cancellation % (canceled / all orders) | Late % by month (line); delivery days by state (bars); late vs on time orders (donut, 2 slices); worst 10 states by late % (bars) |
| 6 | Reviews | How do customers rate us, and what drags the score down? | Average Review; One Star %; Five Star %; Review Rate % (reviewed / delivered orders); Average Review Late (vs Average Review On Time) | Score distribution (columns 1 to 5, no legend); average review by month (line); average review by category (bottom 10 bars); review on time vs late (two bars) |
| 7 | Sellers | Who sells, and who delivers late? | Active Sellers; Revenue per Seller; Late Deliveries % (by seller); Average Review (by seller); Freight % of Revenue | Top 10 sellers by revenue (bars); sellers by state (bars); revenue vs late % per seller (scatter); seller table (revenue, orders, late %, review) |
| 8 | Data table | Can I take the numbers to Excel? | Revenue; Orders; Late Deliveries %; Average Review (the totals of the table below) | Month x state table with revenue, orders, late %, review; Total row |

## Slicers
One global pair on every analysis page, synced: Year (Dropdown), State (Dropdown). No other visible slicers.

## 3-30-300
3 seconds: KPI row. 30 seconds: the four visuals. 300 seconds: Data table and tooltips.

## Navigation
Sidebar buttons: Overview, Sales, Products, Customers, Delivery, Reviews, Sellers, Data table (8 buttons, labels 12 characters or less). Cover has one tile per page.

> **Tricks pass (2026-11-23):** comparison lines in words on three cards, Revenue KPI in millions, Year slicer single select with visible labels, legend and quiet last-year series on the two revenue-by-month charts, Delivery state rankings only for states with 200+ delivered orders, table grid lines. See `06-tricks-plan.md`.
