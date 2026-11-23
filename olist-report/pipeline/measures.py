"""Measures of the Olist model: name, DAX, display folder, format string, one-line description.

Order-level values (review score, delivery days) repeat on every line of an order, so counts are distinct order ids and
averages go over distinct orders: AVERAGEX ( VALUES ( Sales[Order Id] ), ... ).
"""
DELIVERED = "'Order Status'[Order Status] = \"Delivered\""
ON_TIME_OR_LATE = "'Order Status'[Delivery Status] IN { \"On time\", \"Late\" }"
ORDERS = "DISTINCTCOUNT ( Sales[Order Id] )"
UP_DOWN_PCT = '\▲" "0.0%" vs LY";\▼" "0.0%" vs LY";0.0%" vs LY"'


def m(name, dax, folder, desc, fmt=None, hidden=False):
    return dict(name=name, dax=dax.strip("\n"), folder=folder, desc=desc, fmt=fmt, hidden=hidden)


INT, DEC2, PCT, MONEY = "#,##0", "#,##0.00", "0.0%", "#,##0"

MEASURES = [
    # ------------------------------------------------------------ Sales
    m("Revenue", f"CALCULATE ( SUM ( Sales[Price] ), {DELIVERED} )", "Sales", "Item prices of delivered orders, freight excluded.", MONEY),
    m("Orders", f"CALCULATE ( {ORDERS}, {DELIVERED} )", "Sales", "Delivered orders.", INT),
    m("Items Sold", f"CALCULATE ( COUNT ( Sales[Order Line] ), {DELIVERED} )", "Sales", "Items on delivered orders.", INT),
    m("Average Order Value", "DIVIDE ( [Revenue], [Orders] )", "Sales", "Revenue divided by delivered orders.", DEC2),
    m("Average Item Price", "DIVIDE ( [Revenue], [Items Sold] )", "Sales", "Revenue divided by items sold.", DEC2),
    m("Freight", f"CALCULATE ( SUM ( Sales[Freight] ), {DELIVERED} )", "Sales", "Freight charged on delivered orders.", MONEY),
    m("Freight % of Revenue", "DIVIDE ( [Freight], [Revenue] )", "Sales", "Freight as a share of revenue.", PCT),
    m("Share of Revenue %", "DIVIDE ( [Revenue], CALCULATE ( [Revenue], ALLSELECTED ( Product ) ) )", "Sales",
      "Share of the revenue of the selected products.", PCT),
    m("Top Category Share", "DIVIDE ( MAXX ( ALLSELECTED ( Product[Category] ), [Revenue] ), CALCULATE ( [Revenue], ALLSELECTED ( Product ) ) )",
      "Sales", "Revenue share of the best-selling category in the selection.", PCT),
    m("Top Category", "CONCATENATEX ( TOPN ( 1, VALUES ( Product[Category] ), [Revenue] ), Product[Category], \", \" )", "Sales",
      "Name of the category with the most revenue in the selection."),
    m("Categories With Sales", "COUNTROWS ( FILTER ( VALUES ( Product[Category] ), Product[Category] <> \"Unknown\" && [Revenue] > 0 ) )", "Sales",
      "Product categories with revenue (the unknown category is not counted).", INT),
    # ------------------------------------------------------------ Growth
    m("City Latitude", "AVERAGE ( Geography[Latitude] )", "Map", "Hidden: mean latitude of the cities in the cell, for the map (the map needs an aggregate beside Location).", "0.0000", hidden=True),
    m("City Longitude", "AVERAGE ( Geography[Longitude] )", "Map", "Hidden: mean longitude of the cities in the cell, for the map (the map needs an aggregate beside Location).", "0.0000", hidden=True),
    m("Category Leader Colour", "IF ( RANKX ( ALLSELECTED ( Product[Category] ), [Revenue] ) = 1, \"#0A4EE4\", \"#91B4FF\" )", "Colours", "Hidden: hex colour for the chart, the leader in the accent and the rest quiet. Leader by revenue.", hidden=True),
    m("State Orders Leader Colour", "IF ( RANKX ( ALLSELECTED ( Geography[State] ), [Orders] ) = 1, \"#0A4EE4\", \"#91B4FF\" )", "Colours", "Hidden: hex colour for the chart, the leader in the accent and the rest quiet. Leader by orders.", hidden=True),
    m("Weekday Leader Colour", "IF ( RANKX ( ALLSELECTED ( 'Date'[Weekday] ), [Revenue] ) = 1, \"#0A4EE4\", \"#91B4FF\" )", "Colours", "Hidden: hex colour for the chart, the leader in the accent and the rest quiet. Best weekday by revenue.", hidden=True),
    m("Price Band Leader Colour", "IF ( RANKX ( ALLSELECTED ( 'Price Band'[Price Band] ), [Items Sold] ) = 1, \"#0A4EE4\", \"#91B4FF\" )", "Colours", "Hidden: hex colour for the chart, the leader in the accent and the rest quiet. Best price band by items sold.", hidden=True),
    m("City Leader Colour", "IF ( RANKX ( ALLSELECTED ( Geography[City] ), [Customers] ) = 1, \"#0A4EE4\", \"#91B4FF\" )", "Colours", "Hidden: hex colour for the chart, the leader in the accent and the rest quiet. Leader by customers.", hidden=True),
    m("Seller Leader Colour", "IF ( RANKX ( ALLSELECTED ( Seller[Seller] ), [Revenue] ) = 1, \"#0A4EE4\", \"#91B4FF\" )", "Colours", "Hidden: hex colour for the chart, the leader in the accent and the rest quiet. Leader by revenue.", hidden=True),
    m("Late Deliveries % Overall", "CALCULATE ( [Late Deliveries %], ALLSELECTED () )", "Delivery", "Hidden: late deliveries % over everything the slicers allow, the yardstick for colours.", PCT, hidden=True),
    m("Average Delivery Days Overall", "CALCULATE ( [Average Delivery Days], ALLSELECTED () )", "Delivery", "Hidden: average delivery days over everything the slicers allow, the yardstick for colours.", "0.0", hidden=True),
    m("Average Review Overall", "CALCULATE ( [Average Review], ALLSELECTED () )", "Reviews", "Hidden: average review over everything the slicers allow, the yardstick for colours.", "0.00", hidden=True),
    m("Late State Colour", "IF ( [Late Deliveries %] > [Late Deliveries % Overall], \"#C2410C\", \"#8A94A0\" )", "Colours", "Hidden: hex colour, bad when a state is later than the overall rate, else neutral.", hidden=True),
    m("State Delivery Colour", "IF ( [Late Deliveries %] > [Late Deliveries % Overall] && [Average Delivery Days] > [Average Delivery Days Overall], \"#C2410C\", \"#8A94A0\" )", "Colours", "Hidden: hex colour, bad when a state is both slower and later than overall, else neutral.", hidden=True),
    m("Seller Risk Colour", "IF ( [Late Deliveries %] > [Late Deliveries % Overall] && [Average Review] < [Average Review Overall], \"#C2410C\", \"#91B4FF\" )", "Colours", "Hidden: hex colour, bad when a seller is both later and rated lower than overall, else quiet.", hidden=True),
    m("Score Class Colour", "VAR s = SELECTEDVALUE ( Sales[Review Score] ) RETURN SWITCH ( TRUE (), s <= 2, \"#C2410C\", s = 3, \"#8A94A0\", s >= 4, \"#2E9E6B\", \"#8A94A0\" )", "Colours", "Hidden: hex colour of a review score, 1 to 2 bad, 3 neutral, 4 to 5 good.", hidden=True),
    m("Revenue Change vs LY", "VAR Prev = [Revenue LY] RETURN IF ( NOT ISBLANK ( Prev ), [Revenue] - Prev )", "Growth", "Revenue minus revenue of the same days last year; blank unless one year is selected.", "+#,##0;-#,##0;0"),
    m("Last Sale Date", f"CALCULATE ( MAX ( Sales[Purchase Date] ), REMOVEFILTERS (), {DELIVERED} )", "Growth",
      "Purchase date of the latest delivered order, whatever is selected.", "yyyy-mm-dd"),
    m("Revenue LY", """
VAR LastDay = [Last Sale Date]
RETURN
    IF (
        HASONEVALUE ( 'Date'[Year] ),
        CALCULATE ( [Revenue], SAMEPERIODLASTYEAR ( 'Date'[Date] ), KEEPFILTERS ( 'Date'[Date] <= EDATE ( LastDay, -12 ) ) )
    )""", "Growth", "Revenue of the same days one year earlier, up to the last sale date; blank unless one year is selected.", MONEY),
    m("Revenue Growth %", "[Revenue vs LY %]", "Growth", "Revenue change against last year, short form for a card value.", '\▲0.0%;\▼0.0%;0.0%'),
    m("Revenue vs LY %", "VAR Prev = [Revenue LY]\nRETURN IF ( NOT ISBLANK ( Prev ), DIVIDE ( [Revenue] - Prev, Prev ) )", "Growth",
      "Revenue change against the same days of last year.", UP_DOWN_PCT),
    # ------------------------------------------------------------ Customers
    m("Customers", f"CALCULATE ( DISTINCTCOUNT ( Sales[Customer Key] ), {DELIVERED} )", "Customers", "People with a delivered order.", INT),
    m("New Customers", f"CALCULATE ( DISTINCTCOUNT ( Sales[Customer Key] ), {DELIVERED}, Sales[Is First Order] = 1 )", "Customers",
      "People whose first delivered order falls in the selection.", INT),
    m("Returning Customers", f"CALCULATE ( DISTINCTCOUNT ( Sales[Customer Key] ), {DELIVERED}, Sales[Is First Order] = 0 )", "Customers",
      "People with a delivered order that was not their first.", INT),
    m("New Orders", f"CALCULATE ( {ORDERS}, {DELIVERED}, Sales[Is First Order] = 1 )", "Customers", "Delivered orders that are a person's first.", INT),
    m("Returning Orders", f"CALCULATE ( {ORDERS}, {DELIVERED}, Sales[Is First Order] = 0 )", "Customers", "Delivered orders that are not a person's first.", INT),
    m("Repeat Customers %", "DIVIDE ( CALCULATE ( [Returning Customers], ALL ( 'Date' ) ), CALCULATE ( [Customers], ALL ( 'Date' ) ) )", "Customers",
      "Lifetime: people with a second delivered order, out of all people, whatever dates are selected.", PCT),
    m("Revenue per Customer", "DIVIDE ( [Revenue], [Customers] )", "Customers", "Revenue divided by customers.", DEC2),
    m("Orders per Customer", "DIVIDE ( [Orders], [Customers] )", "Customers", "Delivered orders divided by customers.", DEC2),
    # ------------------------------------------------------------ Delivery
    m("Delivered Orders", f"CALCULATE ( {ORDERS}, {ON_TIME_OR_LATE} )", "Delivery", "Orders delivered, with a delivery date.", INT),
    m("Late Orders", f"CALCULATE ( {ORDERS}, 'Order Status'[Delivery Status] = \"Late\" )", "Delivery", "Orders delivered after the estimated date (by date).", INT),
    m("Late Deliveries %", "DIVIDE ( [Late Orders], [Delivered Orders] )", "Delivery", "Late orders as a share of delivered orders.", PCT),
    m("Average Delivery Days", f"CALCULATE ( AVERAGEX ( VALUES ( Sales[Order Id] ), CALCULATE ( MAX ( Sales[Delivery Days] ) ) ), {ON_TIME_OR_LATE} )",
      "Delivery", "Average days from purchase to delivery, per order.", "0.0"),
    m("Average Days Late", "CALCULATE ( AVERAGEX ( VALUES ( Sales[Order Id] ), CALCULATE ( MAX ( Sales[Days Late] ) ) ), 'Order Status'[Delivery Status] = \"Late\" )",
      "Delivery", "Average days past the estimated date, late orders only.", "0.0"),
    m("All Orders", ORDERS, "Delivery", "Every order whatever its status.", INT),
    m("Cancelled Orders", f"CALCULATE ( {ORDERS}, 'Order Status'[Order Status] IN {{ \"Canceled\", \"Unavailable\" }} )", "Delivery",
      "Orders that were canceled or became unavailable.", INT),
    m("Cancellation %", "DIVIDE ( [Cancelled Orders], [All Orders] )", "Delivery", "Cancelled orders as a share of all orders.", PCT),
    # ------------------------------------------------------------ Reviews
    m("Reviewed Orders", f"CALCULATE ( {ORDERS}, {DELIVERED}, KEEPFILTERS ( NOT ISBLANK ( Sales[Review Score] ) ) )", "Reviews",
      "Delivered orders with a review (latest review counts); keeps a score on the axis, so each score shows its own count.", INT),
    m("Review Rate %", "DIVIDE ( [Reviewed Orders], [Orders] )", "Reviews", "Delivered orders that have a review.", PCT),
    m("Average Review", f"CALCULATE ( AVERAGEX ( VALUES ( Sales[Order Id] ), CALCULATE ( MAX ( Sales[Review Score] ) ) ), {DELIVERED} )", "Reviews",
      "Average of the latest review score per delivered order.", "0.00"),
    m("One Star %", f"DIVIDE ( CALCULATE ( {ORDERS}, {DELIVERED}, Sales[Review Score] = 1 ), [Reviewed Orders] )", "Reviews", "Reviewed orders scored 1.", PCT),
    m("Five Star %", f"DIVIDE ( CALCULATE ( {ORDERS}, {DELIVERED}, Sales[Review Score] = 5 ), [Reviewed Orders] )", "Reviews", "Reviewed orders scored 5.", PCT),
    m("Average Review On Time", "CALCULATE ( [Average Review], 'Order Status'[Delivery Status] = \"On time\" )", "Reviews", "Average review of orders delivered on time.", "0.00"),
    m("Average Review Late", "CALCULATE ( [Average Review], 'Order Status'[Delivery Status] = \"Late\" )", "Reviews", "Average review of late orders.", "0.00"),
    m("Review Gap Late vs On Time", "[Average Review Late] - [Average Review On Time]", "Reviews", "Score lost when an order arrives late.",
      '\▲" "0.00" vs on time";\▼" "0.00" vs on time";0.00" vs on time"'),
    m("Review Rank Helper", "IF ( [Orders] >= 200, [Average Review], 6 )", "Reviews",
      "Hidden: orders the lowest-rated chart; categories and sellers under 200 orders rank last.", "0.00", hidden=True),
    m("Review Share %", "DIVIDE ( [Reviewed Orders], CALCULATE ( [Reviewed Orders], ALL ( Sales[Review Score] ) ) )", "Reviews",
      "Share of reviewed orders at each score, within the other filters.", PCT),
    # ------------------------------------------------------------ Payments
    m("Payment Value", f"CALCULATE ( SUM ( Payments[Payment Value] ), {DELIVERED} )", "Payments", "Payments on delivered orders; includes freight and vouchers, so it is above revenue.", MONEY),
    m("Average Payment per Order", f"DIVIDE ( [Payment Value], CALCULATE ( DISTINCTCOUNT ( Payments[Order Id] ), {DELIVERED} ) )", "Payments", "Payment value per delivered order.", DEC2),
    m("Average Payment", f"DIVIDE ( [Payment Value], CALCULATE ( COUNTROWS ( Payments ), {DELIVERED} ) )", "Payments", "Payment value per single payment.", DEC2),
    m("Payment Share %", "DIVIDE ( [Payment Value], CALCULATE ( [Payment Value], ALLSELECTED ( 'Payment Type' ) ) )", "Payments", "Share of payment value by type, within the selection.", PCT),
    m("Credit Card Share %", "DIVIDE ( CALCULATE ( [Payment Value], 'Payment Type'[Payment Type] = \"Credit card\" ), [Payment Value] )", "Payments", "Payment value paid by credit card.", PCT),
    m("Boleto Share %", "DIVIDE ( CALCULATE ( [Payment Value], 'Payment Type'[Payment Type] = \"Boleto\" ), [Payment Value] )", "Payments", "Payment value paid by boleto.", PCT),
    m("Average Installments", f"CALCULATE ( AVERAGE ( Payments[Installments] ), 'Payment Type'[Payment Type] = \"Credit card\", {DELIVERED} )", "Payments", "Average installments of a credit card payment.", "0.0"),
    # ------------------------------------------------------------ Sellers
    m("Active Sellers", f"CALCULATE ( DISTINCTCOUNT ( Sales[Seller Key] ), {DELIVERED} )", "Sellers", "Sellers with a delivered item.", INT),
    m("Revenue per Seller", "DIVIDE ( [Revenue], [Active Sellers] )", "Sellers", "Revenue divided by active sellers.", MONEY),
    # ------------------------------------------------------------ Comparison lines in words (tricks plan rows 3 and 11)
    m("Revenue LY Text", "IF ( ISBLANK ( [Revenue LY] ), BLANK (), \"Last year \" & FORMAT ( [Revenue LY], \"#,##0\" ) )", "Comparisons",
      "Revenue of the same days last year, in words, for the comparison line of a card."),
    m("Returning Customers Text",
      "FORMAT ( CALCULATE ( [Returning Customers], ALL ( 'Date' ) ), \"#,##0\" ) & \" of \" & FORMAT ( CALCULATE ( [Customers], ALL ( 'Date' ) ), \"#,##0\" ) & \" bought again\"",
      "Comparisons", "Lifetime count behind Repeat Customers %, in words, for the comparison line of a card."),
    m("Top Category Text", "\"Leads: \" & [Top Category]", "Comparisons", "Name of the best-selling category, in words, for the comparison line of a card."),
    m("Late Rank Helper", "IF ( [Delivered Orders] >= 200, [Late Deliveries %], -1 )", "Delivery",
      "Hidden: ranks states by late deliveries; those under 200 delivered orders rank last so small samples never reach the top 10.", PCT, hidden=True),
    m("Delivery Days Rank Helper", "IF ( [Delivered Orders] >= 200, [Average Delivery Days], -1 )", "Delivery",
      "Hidden: ranks states by delivery days; those under 200 delivered orders rank last so small samples never reach the top 10.", "0.0", hidden=True),
]

# base measure, kind: pct = percent change, pts = change in percentage points, abs = difference (then decimals shown)
DELTAS = [
    ("Orders", "pct"), ("Average Order Value", "pct"), ("Customers", "pct"), ("Items Sold", "pct"), ("Average Item Price", "pct"),
    ("Revenue per Customer", "pct"), ("New Customers", "pct"), ("Orders per Customer", "pct"), ("Late Orders", "pct"),
    ("Active Sellers", "pct"), ("Revenue per Seller", "pct"), ("Categories With Sales", "pct"),
    ("Average Review", "abs", 2), ("Average Delivery Days", "abs", 1), ("Average Days Late", "abs", 1),
    ("Freight % of Revenue", "pts"), ("Late Deliveries %", "pts"), ("Cancellation %", "pts"), ("One Star %", "pts"),
    ("Five Star %", "pts"), ("Review Rate %", "pts"),
]


def delta_measures():
    out = []
    for name, kind, *dec in DELTAS:
        prev = f"CALCULATE ( [{name}], SAMEPERIODLASTYEAR ( 'Date'[Date] ), KEEPFILTERS ( 'Date'[Date] <= EDATE ( LastDay, -12 ) ) )"
        if kind == "pct":
            value, fmt = "DIVIDE ( [%s] - Prev, Prev )" % name, UP_DOWN_PCT
        elif kind == "pts":
            value, fmt = "( [%s] - Prev ) * 100" % name, '\▲" "0.0" pts vs LY";\▼" "0.0" pts vs LY";0.0" pts vs LY"'
        else:
            n = "0." + "0" * dec[0]
            value, fmt = "[%s] - Prev" % name, '\▲" "%s" vs LY";\▼" "%s" vs LY";%s" vs LY"' % (n, n, n)
        dax = ("VAR LastDay = [Last Sale Date]\nVAR Prev = %s\n"
               "RETURN\n    IF ( HASONEVALUE ( 'Date'[Year] ) && NOT ISBLANK ( Prev ), %s )") % (prev, value)
        what = {"pct": "percent change", "pts": "change in percentage points", "abs": "difference"}[kind]
        out.append(m(f"{name} vs LY", dax, "Comparisons",
                     f"{name}: {what} against the same days of last year; blank unless one year is selected.", fmt))
    # one hidden colour measure per comparison line: good / bad / neutral hex, inverted where lower is better
    lower = {"Late Orders", "Average Delivery Days", "Average Days Late", "Freight % of Revenue", "Late Deliveries %", "Cancellation %", "One Star %"}
    for base, name in [(f"{n} vs LY", n) for n, *_ in DELTAS] + [("Revenue vs LY %", "Revenue"), ("Review Gap Late vs On Time", "")]:
        good, bad = ("#2E9E6B", "#C2410C") if name not in lower else ("#C2410C", "#2E9E6B")
        out.append(m(base + " CF", f"VAR v = [{base}] RETURN IF ( ISBLANK ( v ), \"#8A94A0\", IF ( v > 0, \"{good}\", IF ( v < 0, \"{bad}\", \"#8A94A0\" ) ) )",
                     "Colours", f"Hidden: hex colour of the comparison line {base}, green for good, red for bad, grey for none.", hidden=True))
    return out
