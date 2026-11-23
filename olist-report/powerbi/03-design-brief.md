# Design brief: Olist marketplace report

> **As built (2026-11-22), supersedes the text below where they differ.** Layout: top navigation bar with a KPI strip (picked by the hub from the client name, `layout.json`), not the sidebar. Canvas 1280 x 720 (the frames script set it), so no 1.5 scale; backgrounds are drawn at 2560 x 1440. Icons: 3D Fluent icons named in `spec.json`, not Lucide. The white logo is not used: the logo sits on a white tile. Payment mix is a bar chart (a donut keeps to 3 slices).

Read before writing: look.md (all sections), `powerbi-restyle/references/lessons.md`, and all five images in `references/designs/` (Peaches, Banque Misr x3, Vijay Sales). Brand palette from `brand/brand.json` (logo from olist.com, not the generic site blue).

## What I take from each reference
- **01 Peaches** (the layout I follow): dark sidebar with logo on top, page buttons with an outline icon and a filled accent pill for the active page, "how to read" block at the sidebar foot; light page; one title with a muted subtitle; two small pill slicers top right; KPI row of four cards, one wider hero; a wide trend card with the peak labelled and a segmented control above it.
- **05 Vijay Sales**: round accent icon on every KPI, a row of white cards with the same radius, bar rankings with the value at the bar end, a donut with the total in the centre. Taken as the KPI icon style (soft tile, outline icon), not the red/black palette.
- **02 to 04 Banque Misr**: a card title plus a small uppercase muted sub-title, progress-bar ranking rows, a short labelled insight note inside a card. Not taken: the maroon page, gold gradients.
- Where the references and look.md section 9 disagree, section 9 wins: no saturated page, one accent plus greys, no photos.

## Palette (from the logo)
Page `#F4F6F8`; sidebar `#111B33` (darkest surface); cards white; accent `#0A4EE4` (Olist blue, contrast on white 6.52); soft tile `#E6EDFF`; secondary `#E14E3A` (the orange-red dot of the logo, used only for the highlight and for bad); good `#2E9E6B`; bad `#C2410C`; text `#0F2A3D`; muted `#5B6B7A`. Data colours as `brand.json`. The blue logo is unreadable on the dark sidebar, so the sidebar and cover use the white logo (`brand/logo_white.svg`).

## Grid
Page is 1920 x 1080 (read from `page.json`). Design on the 1280 x 720 grid of look.md section 1 and multiply by 1.5. Sidebar 200 px wide (300 px real); content starts x 216 (324); 16 px gutters; header title at y 8, slicers y 10 (64 high), KPI row y 88 (96 high), body below in two rows. Background rendered at 2560 x 1440, scaling Fit.

## Sidebar (every analysis page, identical)
Olist white logo top-left, thin divider, 8 buttons 160 x 38, 46 apart, icon left, label 12 characters or less, active page a filled accent pill with a white icon. Foot: a "How to read" block ("Selected year against the same days of last year"). Buttons are page-navigation buttons, not the native navigator.

| Button | Lucide icon |
|---|---|
| Overview | layout-dashboard |
| Sales | chart-line |
| Products | package |
| Customers | users |
| Delivery | truck |
| Reviews | star |
| Sellers | store |
| Data table | table |

## Per page: layout, charts, KPI icons
All KPI cards: BI Tricks style per look.md 4b (label, value, delta vs last year, soft icon tile top-right, 30 x 3 accent bar top-left, drawn in the background). KPI card visual keeps 46 px free for the tile. Cards 4 or 5 per row; 5 cards means value 20 pt.

| Page | KPI cards (icon) | Row 2 | Row 3 | Highlight (one) |
|---|---|---|---|---|
| Overview | Revenue (banknote), Orders (shopping-bag), Average Order Value (receipt), Customers (users), Average Review (star) | Revenue by month (smooth line, last year dashed, wide 60%), payment type share (donut, 3 slices, total in centre, 40%) | Top 5 categories by revenue (bars), orders by state top 8 (bars) | the peak month label on the trend |
| Sales | Revenue vs LY % (trending-up), Items Sold (package), Average Item Price (tag), Freight % of Revenue (truck), Revenue per Customer (wallet) | Revenue by month this year vs last (columns), revenue by weekday (columns) | Revenue by state top 10 (bars), revenue by region (donut) | accent column = best weekday, others grey |
| Products | Revenue (banknote), Items Sold (package), Categories With Sales (boxes), Average Item Price (tag), Top Category Share (percent) | Top 10 categories by revenue (bars, wide), revenue trend of the selected category (line) | Price band vs items (columns), category table 9 pt | accent bar = top category |
| Customers | Customers (users), New Customers (user), Repeat Customers % (heart-handshake), Orders per Customer (shopping-cart), Revenue per Customer (wallet) | New vs returning orders by month (columns), customer map by zip prefix (bubble) | Customers by state top 10 (bars), top 10 cities (bars) | the map is the one photo-like card |
| Delivery | Late Deliveries % (alert-triangle), Average Delivery Days (clock), Average Days Late (calendar-days), Late Orders (truck), Cancellation % (x-circle) | Late % by month (smooth line), late vs on time (donut, 2 slices) | Delivery days by state (bars), 10 worst states by late % (bars) | the worst state in accent |
| Reviews | Average Review (star), One Star % (thumbs-up inverted, bad colour), Five Star % (thumbs-up), Review Rate % (eye), Average Review Late (clock) | Score 1 to 5 distribution (columns, no legend), average review by month (smooth line) | Bottom 10 categories by review (bars), on time vs late review (two bars) | one-star column in bad colour |
| Sellers | Active Sellers (store), Revenue per Seller (coins), Late Deliveries % (alert-triangle), Average Review (star), Freight % of Revenue (truck) | Top 10 sellers by revenue (bars), sellers by state (bars) | Revenue vs late % per seller (scatter), seller table 9 pt | accent bar = top seller |
| Data table | none | month x state table, Total row, 9 pt | n/a | n/a |

Question titles above every chart, short (about one character per 7 px of card width). Lines smooth. Dropdown slicers (Year, State), white, radius 12.

## Cover
Dark `#111B33` panel on the left (about 36% width) with the white Olist logo, title "Olist marketplace report", one-line purpose ("Orders, delivery and reviews of a Brazilian marketplace, Sep 2016 to Oct 2018"), a small "Start with Overview" prompt. Right side on the light page: 8 navigation tiles (2 rows of 4), each a white rounded tile with the page icon in a soft accent tile, the page name and its question; transparent navigation buttons placed over the tiles. No stock photo, no home icon as a logo.

## Avoid (look.md section 8)
More than 5 KPIs in a row; more than about 8 visuals per page; several highlights; default grey canvas and square white boxes; native navigator in the sidebar; text boxes shorter than their text; slicers under 56 px high; a Card visual with its own square border on a drawn card; donuts over 3 slices; bars not starting at zero.
