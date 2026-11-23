# Model: Olist marketplace

Built as TMDL by `pipeline/build_model.py` from the tables of `pipeline/build_star.py`. Business names with spaces, keys end in `Key` and are hidden, auto date/time is off.

## Grain, one sentence per table
| Table | Role | One row is |
|---|---|---|
| Sales | fact | an order line, plus one row for each order that has no line (775 canceled or unavailable orders); 113,425 rows |
| Payments | fact | one payment of an order; 103,886 rows |
| Date | dimension | a calendar day, 2016-01-01 to 2018-12-31, marked as the date table |
| Customer | dimension | a person (`customer_unique_id`); 96,096 rows |
| Geography | dimension | a customer city and state, with region and mean coordinates; 4,310 rows |
| Product | dimension | a product, with its English category; plus an Unknown member |
| Seller | dimension | a seller, labelled "Seller" plus the first 6 characters of its id; plus an Unknown member |
| Order Status | junk dimension | a combination of order status and delivery status; 10 rows |
| Price Band | dimension | a price band of an item (0-25 ... 500+, No item) |
| Payment Type | dimension | a payment type |

## Why this shape
- The header (orders) gives context to the lines: its dates, status, review and delivery figures are columns of Sales, repeated on each line. Counts are distinct order ids and averages go over distinct orders, so an order with several lines counts once.
- Facts never relate to each other. Sales and Payments meet only through Date, Customer, Geography and Order Status. The old build joined the facts through the order header, which double counted by category and seller.
- 39 people placed orders from more than one state, so state lives on Geography, which each order points to, not on Customer.

## Relationships (12, many to one, single direction, all active)
Sales to Date, Customer, Geography, Product, Seller, Order Status, Price Band. Payments to Date, Customer, Geography, Order Status, Payment Type.

## What was dropped, and why
Review comments and titles (no use), zip prefix on the fact (the city carries it), product dimensions and photo counts (not asked), seller zip, the 1,000,163 geolocation rows (reduced to one mean point per city in the pipeline, points outside Brazil removed), the order total on payments (derived from the lines).

## Decisions
- Review: each order keeps its latest review by answer time.
- First order: the earliest delivered order of a person; order_id breaks ties (255 people ordered twice in the same second).
- Unknown members exist for orders with no line (no product, no seller).
- Two categories missing from the translation file are named by hand: "Portable Kitchen And Food Preparers", "PC Gamer".
- Order-level measures on a category or seller axis count an order under every category or seller it touches, so those rows do not add up to the total. Revenue and freight do.
