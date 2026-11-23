# Brief: Olist marketplace report

Portfolio / freelancing sample on public data (Kaggle, Brazilian e-commerce by Olist). No client brief, so the audience is a hiring manager or a marketplace operations lead.

## Audience and questions
Reader: a marketplace manager who opens the report to see how the business is doing and where to act.

1. How is the business doing?
2. Are we growing against last year, and where?
3. What sells?
4. Who buys, and do they come back?
5. Do orders arrive when promised?
6. How do customers rate us, and what drags the score down?
7. Who sells, and who delivers late?

## Data (profiled from the CSV headers and row counts, no rows read into the chat)
Folder: D:\Learning\Courses\Other\Instant Software Solution\grad. Orders run 2016-09-04 to 2018-10-17.

| File | Rows | Grain (one row per) |
|---|---|---|
| olist_orders_dataset | 99,441 | order (status, purchase, approval, carrier, delivery, estimated dates) |
| olist_order_items_dataset | 112,650 | order item (order_id + order_item_id): product, seller, price, freight |
| olist_order_payments_dataset | 103,886 | payment of an order (order_id + payment_sequential) |
| olist_order_reviews_dataset | 99,224 | review (an order can have more than one) |
| olist_customers_dataset | 99,441 | customer_id (one per order); customer_unique_id is the person |
| olist_products_dataset | 32,951 | product |
| olist_sellers_dataset | 3,095 | seller |
| product_category_name_translation | 71 | Portuguese category name |
| olist_geolocation_dataset | 1,000,163 | lat/long sample (many per zip prefix) |

Order status: delivered 96,478; shipped 1,107; canceled 625; unavailable 609; invoiced 314; processing 301; created 5; approved 2.

## Business rules (kept from the previous build, `..\olist-report-old\README.md`)
- A sale is an item of a delivered order. Revenue is the item price; freight is shown on its own.
- Late: delivered after the estimated date, compared by date.
- Reviews: one per order, the latest by answer time.
- Payment value includes freight and vouchers, so it is higher than revenue.
- Repeat customer: a person (customer_unique_id) with a second delivered order. First order is the earliest purchase time; order_id breaks ties.
- Year comparison: the selected year against the same days of the year before, up to the last sale date.
- Geolocation: points outside Brazil are dropped before averaging per zip prefix.
- 29 control totals: `..\olist-report-old\checks.md` (Revenue 13,221,498.11; Orders 96,478; Customers 93,358 ...), independent of DAX via `expected_numbers.py`.

## Headline KPIs (4 or 5 per page, every one has a formula and a comparison)
Defined per page in `02-pages.md`. No targets: the client gave none, so deltas compare with last year or with the all-orders figure; nothing is invented.
