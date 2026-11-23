"""Build the Olist star schema as clean CSV files for Power BI, and check it against the control totals.

usage: python pipeline/build_star.py "<folder with the nine Olist CSV files>"

Writes olist-report/data/*.csv (one file per model table, business column names, ISO dates, dot decimals).
Then recomputes every measure of powerbi/control-totals.md from those tables, the way the DAX measures do, and stops
with an error if one differs. Power Query only reads, types and loads these files.

Grain
  Sales     one order line (112,650 rows) plus one row for each order that has no line (775 rows)
  Payments  one payment of an order (103,886 rows)
Facts never relate to each other: they share Date, Customer, Geography and Order Status.
"""
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

SRC = Path(sys.argv[1] if len(sys.argv) > 1 else r"D:\Learning\Courses\Other\Instant Software Solution\grad")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data"
OUT.mkdir(exist_ok=True)
REGIONS = ROOT.parent / "data" / "input" / "regions.csv"
UNKNOWN = "Unknown"
EXTRA_CATEGORIES = {  # two categories missing from the translation file
    "portateis_cozinha_e_preparadores_de_alimentos": "Portable Kitchen And Food Preparers",
    "pc_gamer": "PC Gamer",
}

rd = lambda name, **kw: pd.read_csv(SRC / name, **kw)
orders = rd("olist_orders_dataset.csv", parse_dates=["order_purchase_timestamp", "order_delivered_customer_date", "order_estimated_delivery_date"])
items = rd("olist_order_items_dataset.csv")
cust = rd("olist_customers_dataset.csv")
prod = rd("olist_products_dataset.csv")
sell = rd("olist_sellers_dataset.csv")
trans = rd("product_category_name_translation.csv")
rev = rd("olist_order_reviews_dataset.csv", usecols=["order_id", "review_score", "review_answer_timestamp"], parse_dates=["review_answer_timestamp"])
pay = rd("olist_order_payments_dataset.csv")
geo = rd("olist_geolocation_dataset.csv", usecols=["geolocation_zip_code_prefix", "geolocation_lat", "geolocation_lng"])
regions = pd.read_csv(REGIONS)


def title(s):
    return s.astype("string").str.strip().str.title()


def save(df, name):
    df.to_csv(OUT / name, index=False, encoding="utf-8", date_format="%Y-%m-%d")
    print(f"{name:20s} {len(df):>8,} rows")


# ---------------------------------------------------------------- dimensions
days = pd.date_range("2016-01-01", "2018-12-31")
dim_date = pd.DataFrame({
    "Date": days, "Year": days.year, "Quarter": "Q" + days.quarter.astype(str), "Month Number": days.month,
    "Month": days.strftime("%b"), "Year Month": days.strftime("%Y-%m"),
    "Weekday Number": days.dayofweek + 1, "Weekday": days.strftime("%a"),
    "Month Start": days.to_period("M").to_timestamp(),
    "Quarter Label": "Q" + days.quarter.astype(str) + " " + (days.year % 100).astype(str).str.zfill(2), "Year Quarter": days.year * 10 + days.quarter})
save(dim_date, "Date.csv")

# Geography: one row per customer city and state; coordinates are the mean of its zip prefixes (points outside Brazil dropped)
geo = geo[geo.geolocation_lat.between(-34, 6) & geo.geolocation_lng.between(-74, -34)]
zipxy = geo.groupby("geolocation_zip_code_prefix")[["geolocation_lat", "geolocation_lng"]].mean()
cust = cust.copy()
cust["City"] = title(cust.customer_city)
cust["State"] = cust.customer_state.str.strip().str.upper()
cust["Geography Key"] = cust.State + "|" + cust.City
cust = cust.join(zipxy, on="customer_zip_code_prefix")
dim_geo = (cust.groupby("Geography Key", as_index=False)
           .agg(City=("City", "first"), State=("State", "first"), Latitude=("geolocation_lat", "mean"), Longitude=("geolocation_lng", "mean"))
           .merge(regions.rename(columns={"state": "State", "region": "Region"}), on="State", how="left"))
dim_geo["Region"] = dim_geo.Region.fillna(UNKNOWN)
dim_geo[["Latitude", "Longitude"]] = dim_geo[["Latitude", "Longitude"]].round(4)
dim_geo = dim_geo[["Geography Key", "City", "State", "Region", "Latitude", "Longitude"]]
save(dim_geo, "Geography.csv")

# order-level facts about each order, used by the fact tables below
orders = orders.merge(cust[["customer_id", "customer_unique_id", "Geography Key"]], on="customer_id", how="left")
orders["Date"] = orders.order_purchase_timestamp.dt.normalize()
delivered_day = orders.order_delivered_customer_date.dt.normalize()
estimated_day = orders.order_estimated_delivery_date.dt.normalize()
orders["Status"] = orders.order_status.str.title()
is_sale = orders.order_status == "delivered"
has_date = is_sale & delivered_day.notna()
late = has_date & (delivered_day > estimated_day)
orders["Delivery Status"] = np.where(~is_sale, "Not delivered", np.where(~has_date, "No date", np.where(late, "Late", "On time")))
orders["Delivery Days"] = (delivered_day - orders.Date).dt.days.where(has_date)
orders["Days Late"] = (delivered_day - estimated_day).dt.days.where(late)
orders["Order Status Key"] = orders.Status + "|" + orders["Delivery Status"]
first = (orders[is_sale].sort_values(["customer_unique_id", "order_purchase_timestamp", "order_id"])
         .drop_duplicates("customer_unique_id").order_id)  # earliest delivered order of each person, order_id breaks ties
orders["Is First Order"] = np.where(is_sale, orders.order_id.isin(first).astype(int), np.nan)
latest_review = rev.sort_values("review_answer_timestamp", ascending=False).drop_duplicates("order_id")
orders = orders.merge(latest_review[["order_id", "review_score"]].rename(columns={"review_score": "Review Score"}), on="order_id", how="left")

dim_status = (orders[["Order Status Key", "Status", "Delivery Status"]].drop_duplicates().rename(columns={"Status": "Order Status"})
              .sort_values("Order Status Key"))
save(dim_status, "Order Status.csv")

persons = orders[is_sale].groupby("customer_unique_id").size()
dim_cust = pd.DataFrame({"Customer Key": cust.customer_unique_id.drop_duplicates().sort_values()})
dim_cust["Customer Type"] = dim_cust["Customer Key"].map(persons).map(lambda n: "No completed order" if pd.isna(n) else ("Repeat" if n > 1 else "One-time"))
save(dim_cust, "Customer.csv")

cat = dict(zip(trans.product_category_name, title(trans.product_category_name_english.str.replace("_", " "))))
cat.update(EXTRA_CATEGORIES)
dim_prod = pd.DataFrame({"Product Key": prod.product_id, "Category": prod.product_category_name.map(cat).fillna(UNKNOWN)})
dim_prod = pd.concat([dim_prod, pd.DataFrame({"Product Key": [UNKNOWN], "Category": [UNKNOWN]})], ignore_index=True)
save(dim_prod, "Product.csv")

dim_sell = pd.DataFrame({"Seller Key": sell.seller_id, "Seller": "Seller " + sell.seller_id.str[:6],
                         "Seller City": title(sell.seller_city), "Seller State": sell.seller_state.str.upper()})
dim_sell = pd.concat([dim_sell, pd.DataFrame({"Seller Key": [UNKNOWN], "Seller": [UNKNOWN], "Seller City": [UNKNOWN], "Seller State": [UNKNOWN]})], ignore_index=True)
assert dim_sell.Seller.is_unique, "seller label collides"
save(dim_sell, "Seller.csv")

bands = [("0-25", 0, 25), ("25-50", 25, 50), ("50-100", 50, 100), ("100-200", 100, 200), ("200-500", 200, 500), ("500+", 500, 1e12)]
labels = [b[0] for b in bands] + ["No item"]
dim_band = pd.DataFrame({"Price Band Key": labels, "Price Band": labels, "Band Order": range(1, len(bands) + 2)})
save(dim_band, "Price Band.csv")

ptype = {"credit_card": "Credit card", "boleto": "Boleto", "voucher": "Voucher", "debit_card": "Debit card", "not_defined": "Not defined"}
dim_pay = pd.DataFrame({"Payment Type Key": list(ptype), "Payment Type": list(ptype.values())})
save(dim_pay, "Payment Type.csv")

# ---------------------------------------------------------------- facts
orders = orders.rename(columns={"Date": "Purchase Date"})
ctx = orders[["order_id", "customer_unique_id", "Geography Key", "Purchase Date", "Order Status Key", "Review Score", "Delivery Days", "Days Late", "Is First Order"]]
lines = orders[["order_id"]].merge(items, on="order_id", how="left")  # left: orders without a line keep one row
lines["Price Band Key"] = "No item"
has_line = lines.price.notna()
lines.loc[has_line, "Price Band Key"] = pd.cut(lines.price[has_line], [b[1] for b in bands] + [1e12], right=False, labels=[b[0] for b in bands]).astype(str)
lines["product_id"] = lines.product_id.fillna(UNKNOWN)
lines["seller_id"] = lines.seller_id.fillna(UNKNOWN)
sales = lines.merge(ctx, on="order_id", how="left", validate="many_to_one")
sales = sales.rename(columns={"order_id": "Order Id", "order_item_id": "Order Line", "customer_unique_id": "Customer Key", "product_id": "Product Key",
                              "seller_id": "Seller Key", "price": "Price", "freight_value": "Freight"})
sales = sales[["Order Id", "Order Line", "Purchase Date", "Customer Key", "Geography Key", "Product Key", "Seller Key", "Order Status Key", "Price Band Key",
               "Price", "Freight", "Review Score", "Delivery Days", "Days Late", "Is First Order"]]
for c in ("Order Line", "Review Score", "Delivery Days", "Days Late", "Is First Order"):
    sales[c] = sales[c].astype("Int64")
assert len(sales) == len(items) + (~orders.order_id.isin(items.order_id)).sum(), "sales row count"
save(sales, "Sales.csv")

payments = pay.merge(ctx[["order_id", "customer_unique_id", "Geography Key", "Purchase Date", "Order Status Key"]], on="order_id", how="left", validate="many_to_one")
payments = payments.rename(columns={"order_id": "Order Id", "payment_sequential": "Payment Sequence", "customer_unique_id": "Customer Key",
                                    "payment_type": "Payment Type Key", "payment_installments": "Installments", "payment_value": "Payment Value"})
payments = payments[["Order Id", "Payment Sequence", "Purchase Date", "Customer Key", "Geography Key", "Order Status Key", "Payment Type Key", "Installments", "Payment Value"]]
assert len(payments) == len(pay)
save(payments, "Payments.csv")

# ---------------------------------------------------------------- referential integrity: every fact key exists in its dimension
for fact, col, dim, key in [(sales, "Customer Key", dim_cust, "Customer Key"), (sales, "Geography Key", dim_geo, "Geography Key"),
                            (sales, "Product Key", dim_prod, "Product Key"), (sales, "Seller Key", dim_sell, "Seller Key"),
                            (sales, "Order Status Key", dim_status, "Order Status Key"), (sales, "Price Band Key", dim_band, "Price Band Key"),
                            (sales, "Purchase Date", dim_date, "Date"), (payments, "Payment Type Key", dim_pay, "Payment Type Key"),
                            (payments, "Customer Key", dim_cust, "Customer Key"), (payments, "Geography Key", dim_geo, "Geography Key"),
                            (payments, "Order Status Key", dim_status, "Order Status Key"), (payments, "Purchase Date", dim_date, "Date")]:
    missing = (~fact[col].isin(dim[key])).sum()
    assert missing == 0, f"{col}: {missing} fact rows without a dimension row"
for d, k in [(dim_cust, "Customer Key"), (dim_geo, "Geography Key"), (dim_prod, "Product Key"), (dim_sell, "Seller Key"),
             (dim_status, "Order Status Key"), (dim_band, "Price Band Key"), (dim_pay, "Payment Type Key"), (dim_date, "Date")]:
    assert d[k].is_unique, f"{k} is not unique"

# ---------------------------------------------------------------- control totals, computed from the built tables the way the measures do
S = sales.merge(dim_status, on="Order Status Key")
P = payments.merge(dim_status, on="Order Status Key")
sale = S[S["Order Status"] == "Delivered"]
dd = S[S["Delivery Status"].isin(["On time", "Late"])]


def per_order(df, col):  # average over distinct orders, as AVERAGEX ( VALUES ( order ), ... ) does
    return df.groupby("Order Id")[col].max().mean()


n_orders = sale["Order Id"].nunique()
revenue = sale.Price.sum()
persons_n = sale["Customer Key"].nunique()
returning = sale[sale["Is First Order"] == 0]["Customer Key"].nunique()
rated = sale.dropna(subset=["Review Score"]).drop_duplicates("Order Id")
ps = P[P["Order Status"] == "Delivered"]
cc = ps[ps["Payment Type Key"] == "credit_card"]
got = {
    "Revenue": f"{revenue:,.2f}", "Orders": f"{n_orders:,}", "Items Sold": f"{sale['Order Line'].count():,}",
    "Average Order Value": f"{revenue / n_orders:,.2f}", "Freight % of Revenue": f"{sale.Freight.sum() / revenue:.1%}",
    "Customers": f"{persons_n:,}", "New Customers": f"{sale[sale['Is First Order'] == 1]['Customer Key'].nunique():,}",
    "Returning Customers": f"{returning:,}", "Repeat Customers %": f"{returning / persons_n:.1%}",
    "Delivered Orders": f"{dd['Order Id'].nunique():,}", "Late Orders": f"{S[S['Delivery Status'] == 'Late']['Order Id'].nunique():,}",
    "Late Deliveries %": f"{S[S['Delivery Status'] == 'Late']['Order Id'].nunique() / dd['Order Id'].nunique():.1%}",
    "Average Delivery Days": f"{per_order(dd, 'Delivery Days'):.1f}",
    "Average Days Late": f"{per_order(S[S['Delivery Status'] == 'Late'], 'Days Late'):.1f}",
    "All Orders": f"{S['Order Id'].nunique():,}",
    "Cancellation %": f"{S[S['Order Status'].isin(['Canceled', 'Unavailable'])]['Order Id'].nunique() / S['Order Id'].nunique():.1%}",
    "Active Sellers": f"{sale['Seller Key'].nunique():,}",
    "Reviewed Orders": f"{len(rated):,}", "Review Rate %": f"{len(rated) / n_orders:.1%}",
    "Average Review": f"{rated['Review Score'].mean():.2f}", "One Star %": f"{(rated['Review Score'] == 1).mean():.1%}",
    "Five Star %": f"{(rated['Review Score'] == 5).mean():.1%}",
    "Average Review On Time": f"{rated[rated['Delivery Status'] == 'On time']['Review Score'].mean():.2f}",
    "Average Review Late": f"{rated[rated['Delivery Status'] == 'Late']['Review Score'].mean():.2f}",
    "Payment Value": f"{ps['Payment Value'].sum():,.2f}", "Average Payment per Order": f"{ps['Payment Value'].sum() / n_orders:,.2f}",
    "Credit Card Share %": f"{cc['Payment Value'].sum() / ps['Payment Value'].sum():.1%}",
    "Boleto Share %": f"{ps[ps['Payment Type Key'] == 'boleto']['Payment Value'].sum() / ps['Payment Value'].sum():.1%}",
    "Average Installments": f"{cc.Installments.mean():.1f}",
}
want = dict(re.findall(r"^\| (.+?) \| (.+?) \|$", (ROOT / "powerbi" / "control-totals.md").read_text(encoding="utf-8"), re.M))
bad = [(k, v, want.get(k)) for k, v in got.items() if want.get(k) != v]
for k, v in got.items():
    print(("ok    " if want.get(k) == v else "FAIL  ") + f"{k:28s} {v:>16s}   expected {want.get(k)}")
FAILED = "control totals differ: %s" % bad if bad or len(got) != 29 else None


# ---------------------------------------------------------------- expected "vs LY" values for the year 2018 (Date[Year] = 2018)
last_day = sale["Purchase Date"].max()
ly_end = last_day - pd.DateOffset(years=1)
cur = lambda df: df[df["Purchase Date"].dt.year == 2018]
ly = lambda df: df[(df["Purchase Date"].dt.year == 2017) & (df["Purchase Date"] <= ly_end)]
S["Purchase Date"] = pd.to_datetime(S["Purchase Date"]); sale = S[S["Order Status"] == "Delivered"]; dd = S[S["Delivery Status"].isin(["On time", "Late"])]
late_pct = lambda f: f[f["Delivery Status"] == "Late"]["Order Id"].nunique() / f["Order Id"].nunique()
avg_rev = lambda f: f.dropna(subset=["Review Score"]).drop_duplicates("Order Id")["Review Score"].mean()
rev_c, rev_p = cur(sale).Price.sum(), ly(sale).Price.sum()
ord_c, ord_p = cur(sale)["Order Id"].nunique(), ly(sale)["Order Id"].nunique()
exp18 = {
    "Last Sale Date": last_day.strftime("%Y-%m-%d"), "Revenue": f"{rev_c:,.2f}", "Revenue LY": f"{rev_p:,.2f}",
    "Revenue vs LY %": f"{(rev_c - rev_p) / rev_p:.1%}", "Orders vs LY": f"{(ord_c - ord_p) / ord_p:.1%}",
    "Late Deliveries % vs LY (pts)": f"{(late_pct(cur(dd)) - late_pct(ly(dd))) * 100:.1f}",
    "Average Review vs LY": f"{avg_rev(cur(sale)) - avg_rev(ly(sale)):.2f}",
}
out = ["# Expected comparison values with Date[Year] = 2018", "",
       "Computed in pandas from the built tables: 2018 against 2017 up to the same day (Last Sale Date minus 12 months).", "",
       "| Measure | Expected |", "|---|---|"] + [f"| {k} | {v} |" for k, v in exp18.items()]
(ROOT / "powerbi" / "control-totals-2018.md").write_text(chr(10).join(out) + chr(10), encoding="utf-8")
print(chr(10).join(out[5:]))

if FAILED:
    sys.exit(FAILED)
