"""Compute, in pandas straight from the Olist CSVs, the value each card should show with no filters. Writes powerbi/control-totals.md."""
import sys
from pathlib import Path
import pandas as pd

D = Path(sys.argv[1] if len(sys.argv) > 1 else r"D:\Learning\Courses\Other\Instant Software Solution\grad")
o = pd.read_csv(D / "olist_orders_dataset.csv", parse_dates=["order_purchase_timestamp", "order_delivered_customer_date", "order_estimated_delivery_date"])
i = pd.read_csv(D / "olist_order_items_dataset.csv")
c = pd.read_csv(D / "olist_customers_dataset.csv")
o = o.merge(c[["customer_id", "customer_unique_id"]], on="customer_id")
o["order_date"] = o.order_purchase_timestamp.dt.normalize()
o["delivered"] = o.order_delivered_customer_date.dt.normalize()
o["estimated"] = o.order_estimated_delivery_date.dt.normalize()
o["is_sale"] = o.order_status == "delivered"
dd = o.is_sale & o.delivered.notna()
o["late"] = dd & (o.delivered > o.estimated)
o["days"] = (o.delivered - o.order_date).dt.days.where(dd)
o["days_late"] = (o.delivered - o.estimated).dt.days.where(o.late)
sales = o[o.is_sale]
sales = sales.sort_values(["customer_unique_id", "order_purchase_timestamp", "order_id"])
sales["first"] = ~sales.duplicated("customer_unique_id")  # same tie-break as Power Query: order_id
li = i.merge(sales[["order_id"]], on="order_id")
persons = sales.customer_unique_id.nunique()
repeat = sales[~sales["first"]].customer_unique_id.nunique()
rows = [
    ("Revenue", f"{li.price.sum():,.2f}"), ("Orders", f"{len(sales):,}"), ("Items Sold", f"{len(li):,}"),
    ("Average Order Value", f"{li.price.sum() / len(sales):,.2f}"), ("Freight % of Revenue", f"{li.freight_value.sum() / li.price.sum():.1%}"),
    ("Customers", f"{persons:,}"), ("New Customers", f"{sales[sales['first']].customer_unique_id.nunique():,}"),
    ("Returning Customers", f"{repeat:,}"), ("Repeat Customers %", f"{repeat / persons:.1%}"),
    ("Delivered Orders", f"{int(dd.sum()):,}"), ("Late Orders", f"{int(o.late.sum()):,}"),
    ("Late Deliveries %", f"{o.late.sum() / dd.sum():.1%}"), ("Average Delivery Days", f"{o.days.mean():.1f}"),
    ("Average Days Late", f"{o.days_late.mean():.1f}"), ("All Orders", f"{len(o):,}"),
    ("Cancellation %", f"{o.order_status.isin(['canceled', 'unavailable']).mean():.1%}"),
    ("Active Sellers", f"{li.seller_id.nunique():,}"),
]
rv = pd.read_csv(D / "olist_order_reviews_dataset.csv", usecols=["order_id", "review_score", "review_answer_timestamp"], parse_dates=["review_answer_timestamp"])
rv = rv.sort_values("review_answer_timestamp", ascending=False).drop_duplicates("order_id")
s = sales.merge(rv[["order_id", "review_score"]], on="order_id", how="left")
rated = s.dropna(subset=["review_score"])
pay = pd.read_csv(D / "olist_order_payments_dataset.csv").merge(sales[["order_id"]], on="order_id")
pv = pay.payment_value.sum()
cc = pay[pay.payment_type == "credit_card"]
rows += [
    ("Reviewed Orders", f"{len(rated):,}"), ("Review Rate %", f"{len(rated) / len(s):.1%}"),
    ("Average Review", f"{rated.review_score.mean():.2f}"), ("One Star %", f"{(rated.review_score == 1).mean():.1%}"),
    ("Five Star %", f"{(rated.review_score == 5).mean():.1%}"),
    ("Average Review On Time", f"{rated[rated.late == False][rated.delivered.notna()].review_score.mean():.2f}"),
    ("Average Review Late", f"{rated[rated.late].review_score.mean():.2f}"),
    ("Payment Value", f"{pv:,.2f}"), ("Average Payment per Order", f"{pv / len(sales):,.2f}"),
    ("Credit Card Share %", f"{cc.payment_value.sum() / pv:.1%}"),
    ("Boleto Share %", f"{pay[pay.payment_type == 'boleto'].payment_value.sum() / pv:.1%}"),
    ("Average Installments", f"{cc.payment_installments.mean():.1f}"),
]
out = ["# Control totals: what each measure must show with no filter selected", "",
       "Computed in pandas from the Olist CSV files by `expected_numbers.py`, independently of Power Query and DAX.", "",
       "| Measure | Expected |", "|---|---|"] + [f"| {n} | {v} |" for n, v in rows]
(Path(__file__).resolve().parents[1] / "powerbi" / "control-totals.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(out))
