"""S11: put the real visuals on the drawn pages: KPI cards, slicers and charts, at the card rectangles in powerbi/layout.json.

usage: python pipeline/build_pages.py

Writes only its own visuals (folders kpi*, chart*, slicer*) next to the ff_* frames of make_frames.py; reruns replace them.
Every visual is transparent (the card is drawn in the page background) and inset 10 px inside its card.
"""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
REPORT = ROOT / "olist_e_commerce_report.Report" / "definition"
LAYOUT = json.load(open(ROOT / "powerbi" / "layout.json", encoding="utf-8"))
SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.13.0/schema.json"
TEXT, MUTED, EDGE = "#0F2A3D", "#5B6B7A", "#E3E8EE"
INSET = 10


# ---------------------------------------------------------------- small builders
def lit(v):
    return {"expr": {"Literal": {"Value": v}}}


def fld(kind, table, name):
    return {kind: {"Expression": {"SourceRef": {"Entity": table}}, "Property": name}}


def col(table, name):
    return fld("Column", table, name)


def mea(name):
    return fld("Measure", "_Measures", name)


def proj(field, active=False):
    (kind, body), = field.items()
    table, name = body["Expression"]["SourceRef"]["Entity"], body["Property"]
    p = {"field": field, "queryRef": f"{table}.{name}", "nativeQueryRef": name}
    if active:
        p["active"] = True
    return p


def roles(**kw):
    return {"queryState": {r: {"projections": [proj(f) for f in (fs if isinstance(fs, list) else [fs])]} for r, fs in kw.items()}}


def container(title=None, alt=None, white=False):
    off = {"properties": {"show": lit("false")}}
    o = {"background": [{"properties": {"show": lit("true"), "color": {"solid": {"color": lit("'#FFFFFF'")}}, "transparency": lit("0D")}}] if white
         else [off],
         "border": [{"properties": {"show": lit("true"), "color": {"solid": {"color": lit("'%s'" % EDGE)}}, "radius": lit("12D")}}] if white else [off],
         "dropShadow": [off], "visualHeader": [off]}
    if title:
        o["title"] = [{"properties": {"show": lit("true"), "text": lit("'%s'" % title.replace("'", "''")), "fontColor": {"solid": {"color": lit("'%s'" % TEXT)}},
                                      "fontSize": lit("11D"), "bold": lit("true"), "fontFamily": lit("'Segoe UI Semibold'"), "alignment": lit("'left'")}}]
    else:
        o["title"] = [off]
    o["subTitle"] = [off]
    if alt:
        o["general"] = [{"properties": {"altText": lit("'%s'" % alt.replace("'", "''"))}}]
    return o


def topn(table, column, measure, n, direction=2):
    """Visual filter: the n members of table[column] with the highest (direction 2) or lowest (1) measure."""
    sub = {"Version": 2, "From": [{"Name": "t", "Entity": table, "Type": 0}, {"Name": "m", "Entity": "_Measures", "Type": 0}],
           "Select": [{"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": column}, "Name": "field"}],
           "OrderBy": [{"Direction": direction, "Expression": {"Measure": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": measure}}}], "Top": n}
    return {"filters": [{"name": "topn_%s_%s" % (column.replace(" ", ""), n), "field": col(table, column), "type": "TopN",
                         "filter": {"Version": 2, "From": [{"Name": "subquery", "Expression": {"Subquery": {"Query": sub}}, "Type": 2}, {"Name": "t", "Entity": table, "Type": 0}],
                                    "Where": [{"Condition": {"In": {"Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": column}}],
                                                                    "Table": {"SourceRef": {"Source": "subquery"}}}}}]},
                         "howCreated": "User"}]}


def sort_by(field, direction="Descending"):
    return {"sort": [{"field": field, "direction": direction}], "isDefaultSort": False}


def axis_small():
    return {"categoryAxis": [{"properties": {"fontSize": lit("9D"), "labelColor": {"solid": {"color": lit("'%s'" % MUTED)}}, "gridlineShow": lit("false")}}],
            "valueAxis": [{"properties": {"show": lit("false"), "gridlineShow": lit("false")}}],
            "labels": [{"properties": {"show": lit("true"), "fontSize": lit("9D"), "color": {"solid": {"color": lit("'%s'" % TEXT)}}}}],
            "legend": [{"properties": {"show": lit("false")}}]}


GREY_LY = "#C9D3DC"


def two_series(o, current, last_year, dashed=False):
    """Legend on top, the current measure in the accent, the last-year measure in the quiet grey (series selected by metadata)."""
    o = dict(o)
    o["legend"] = [{"properties": {"show": lit("true"), "position": lit("'Top'"), "fontSize": lit("9D")}}]
    o["labels"] = [{"properties": {"show": lit("false")}}]
    o["valueAxis"] = [{"properties": {"show": lit("true"), "fontSize": lit("9D"), "gridlineShow": lit("true")}}]
    fill = lambda c: {"solid": {"color": lit("'%s'" % c)}}
    o["dataPoint"] = [{"properties": {"fill": fill("#0A4EE4")}, "selector": {"metadata": "_Measures." + current}},
                      {"properties": {"fill": fill(GREY_LY)}, "selector": {"metadata": "_Measures." + last_year}}]
    if dashed:
        o["lineStyles"] = [{"properties": {"lineChartType": lit("'smooth'"), "interpolationSmooth": lit("'monotoneX'")}},
                           {"properties": {"lineStyle": lit("'dashed'")}, "selector": {"metadata": "_Measures." + last_year}}]
    return o


def straight(o):
    o["lineStyles"] = [{"properties": {"lineChartType": lit("'straight'")}}]
    return o


def smooth(o):
    o["lineStyles"] = [{"properties": {"lineChartType": lit("'smooth'"), "interpolationSmooth": lit("'monotoneX'")}}]
    return o


# ---------------------------------------------------------------- visual kinds
def chart(kind, query, title, alt, objects=None, filters=None, sort=None):
    q = dict(query)
    if sort:
        q["sortDefinition"] = sort
    v = {"visualType": kind, "query": q, "objects": objects or {}, "visualContainerObjects": container(title, alt), "drillFilterOtherVisuals": True}
    d = {"visual": v}
    if filters:
        d["filterConfig"] = filters
    return d


def table(fields, title, alt, sort_field=None, total=False, padding=4, widths=()):
    o = {"values": [{"properties": {"fontSize": lit("9D")}}], "columnHeaders": [{"properties": {"fontSize": lit("9D"), "bold": lit("true")}}],
         "total": [{"properties": {"show": lit("true" if total else "false")}}],
         "grid": [{"properties": {"gridHorizontal": lit("true"), "gridHorizontalColor": {"solid": {"color": lit("'%s'" % EDGE)}}, "rowPadding": lit("%dD" % padding)}}]}
    if widths:
        o["columnWidth"] = [{"properties": {"value": lit("%dD" % w)}, "selector": {"metadata": proj(f)["queryRef"]}} for f, w in zip(fields, widths)]
    return chart("tableEx", roles(Values=fields), title, alt, o, sort=sort_by(mea(sort_field)) if sort_field else None)


YEAR, STATE = col("Date", "Year"), col("Geography", "State")


def slicer(field, name, group, default=None, single=False):
    o = {"data": [{"properties": {"mode": lit("'Dropdown'")}}],
         "header": [{"properties": {"show": lit("true"), "textSize": lit("9D"), "fontColor": {"solid": {"color": lit("'%s'" % MUTED)}}}}],
         "items": [{"properties": {"textSize": lit("10D"), "fontColor": {"solid": {"color": lit("'%s'" % TEXT)}}}}],
         "general": [{"properties": {}}]}
    if default is not None:
        (_, body), = field.items()
        o["general"][0]["properties"]["filter"] = {"filter": {"Version": 2, "From": [{"Name": "d", "Entity": body["Expression"]["SourceRef"]["Entity"], "Type": 0}],
                                                              "Where": [{"Condition": {"In": {"Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "d"}}, "Property": body["Property"]}}],
                                                                                              "Values": [[{"Literal": {"Value": default}}]]}}}]}}
    if single:
        o["selection"] = [{"properties": {"singleSelect": lit("true")}}]
    q = {"queryState": {"Values": {"projections": [proj(field, active=True)]}}}
    return {"visual": {"visualType": "slicer", "query": q, "objects": o, "visualContainerObjects": container(None, "%s slicer" % name, white=True),
                       "drillFilterOtherVisuals": True,
                       "syncGroup": {"groupName": group, "fieldChanges": True, "filterChanges": True}}}


from measures import MEASURES as _BASE, delta_measures as _DELTAS  # noqa: E402

CF_MEASURES = {m_["name"] for m_ in _BASE + _DELTAS() if m_["name"].endswith(" CF")}


def kpi(measure, ref, alt, millions=False):
    """Card visual: label, value and a comparison line. Shape follows the worked template card-kpi-with-yoy.md:
    overrides use selector id default, the comparison line is the reference label Detail, tied to the main measure by metadata and a field id."""
    fid = "ref-" + measure.replace(" ", "").replace("%", "pct")
    main = "_Measures." + measure
    flit = lambda v: {"expr": {"Literal": {"Value": v}}}
    off = lambda sel=True: [{"properties": {"show": flit("false")}, **({"selector": {"id": "default"}} if sel else {})}]
    q = {"queryState": {"Data": {"projections": [proj(mea(measure))]}}}
    o = {
        "outline": off(), "borderCustom": off(), "divider": off(), "fillCustom": off(False), "shadowCustom": off(False), "glowCustom": off(False),
        "label": [{"properties": {"fontSize": lit("9D"), "fontColor": {"solid": {"color": lit("'%s'" % MUTED)}}}, "selector": {"id": "default"}}],
        "value": [{"properties": {"fontSize": lit("20D"), "fontFamily": lit("'Segoe UI Semibold'"), "color": {"solid": {"color": lit("'%s'" % TEXT)}},
                                  **({"labelDisplayUnits": lit("1000000D"), "labelPrecision": lit("1L")} if millions else {})}}],
        "spacing": [{"properties": {"verticalSpacing": lit("0L")}, "selector": {"id": "default"}}],
        "padding": [{"properties": {"paddingUniform": lit("0L")}, "selector": {"id": "default"}}],
        "cards": [{"properties": {"showLabel": lit("true")}}],
    }
    if ref:
        q["queryState"]["ReferenceLabels"] = {"projections": [proj(mea(ref))]}
        colour = ({"solid": {"color": {"expr": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": ref + " CF"}}}}}
                  if ref + " CF" in CF_MEASURES else {"solid": {"color": lit("'%s'" % MUTED)}})
        sel = {"metadata": main, "id": fid}
        o["referenceLabel"] = [{"properties": {"backgroundShow": lit("false"), "paddingUniform": lit("0L")}, "selector": {"id": "default"}}]
        o["referenceLabelDetail"] = [
            {"properties": {"show": lit("true")}, "selector": dict(sel)},
            {"properties": {"detailValue": {"expr": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": ref}}},
                            "detailFontColor": colour, "detailFontSize": lit("9D"), "enableBackground": lit("false")},
             "selector": {**sel, "data": [{"dataViewWildcard": {"matchingOption": 0}}]}}]
        o["referenceLabelTitle"] = [{"properties": {"show": lit("false")}, "selector": dict(sel)}]
    return {"visual": {"visualType": "cardVisual", "query": q, "objects": o, "visualContainerObjects": container(None, alt), "drillFilterOtherVisuals": True}}


# ---------------------------------------------------------------- the pages: KPI (measure, comparison) and the four charts
D, G, P, S_, ST, PB = "Date", "Geography", "Product", "Seller", "Order Status", "Price Band"
vsly = lambda m: (m, m + " vs LY")
# ---------------------------------------------------------------- colour helpers (property shapes copied from the pbir-format examples)
ACCENT, QUIET, BAD, GOOD, NEUTRAL = "#0A4EE4", "#91B4FF", "#C2410C", "#2E9E6B", "#8A94A0"


def solid(c):
    return {"solid": {"color": lit("'%s'" % c)}}


def dp_measure(name):
    """Fill of each mark from a measure that returns a hex colour (scatterChart example, selector dataViewWildcard 1)."""
    return {"properties": {"fill": {"solid": {"color": {"expr": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": name}}}}}},
            "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}]}}


def dp_member(table, column, value, colour):
    """Fill of one category member (donutChart example, selector scopeId Comparison)."""
    return {"properties": {"fill": solid(colour)},
            "selector": {"data": [{"scopeId": {"Comparison": {"ComparisonKind": 0, "Left": col(table, column), "Right": {"Literal": {"Value": "'%s'" % value}}}}}]}}


def dp_series(measure, colour):
    """Fill of one measure series (lineChart example, selector metadata)."""
    return {"properties": {"fill": solid(colour)}, "selector": {"metadata": "_Measures." + measure}}


def with_legend(o, position="Top"):
    o = dict(o)
    o["legend"] = [{"properties": {"show": lit("true"), "position": lit("'%s'" % position), "fontSize": lit("9D")}}]
    return o


def bars(color_measure):
    o = axis_small()
    o["categoryAxis"] = [{"properties": {"fontSize": lit("9D"), "labelColor": {"solid": {"color": lit("'%s'" % MUTED)}}, "gridlineShow": lit("false"), "maxMarginFactor": lit("45L")}}]
    o["dataPoint"] = [dp_measure(color_measure)]
    return o


def trend(o):
    o = dict(o)
    o["trend"] = [{"properties": {"show": lit("true"), "lineColor": solid(NEUTRAL), "transparency": lit("20D"), "style": lit("'dashed'")}}]
    return o


def labels_on(o):
    o = dict(o)
    o["labels"] = [{"properties": {"show": lit("true"), "fontSize": lit("9D")}}]
    return o


MEMBERS_PAY = [("Credit card", ACCENT), ("Boleto", "#E14E3A"), ("Voucher", QUIET), ("Debit card", "#5B6B7A"), ("Not defined", "#C9D3DC")]
PAY, ST_, CU = "Payment Type", "Order Status", "Customer"

PAGES = {
    "pg01Overview": dict(
        kpis=[("Revenue", "Revenue vs LY %"), vsly("Orders"), vsly("Average Order Value"), vsly("Customers"), vsly("Average Review")],
        charts=[
            chart("lineChart", roles(Category=col(D, "Month Start"), Y=[mea("Revenue"), mea("Revenue LY")]), "Is revenue growing month by month?",
                  "Line chart of revenue by month against last year", two_series(smooth(axis_small()), "Revenue", "Revenue LY", dashed=True)),
            chart("treemap", roles(Group=col(PAY, "Payment Type"), Values=mea("Payment Value")), "How do customers pay?", "Treemap of payment value by payment type",
                  {**with_legend({}), "dataPoint": [dp_member(PAY, "Payment Type", v, c) for v, c in MEMBERS_PAY]}),
            chart("clusteredBarChart", roles(Category=col(P, "Category"), Y=mea("Revenue")), "Which categories earn most?", "Revenue of the top 5 categories",
                  bars("Category Leader Colour"), topn(P, "Category", "Revenue", 5), sort_by(mea("Revenue"))),
            chart("clusteredBarChart", roles(Category=col(G, "State"), Y=mea("Orders")), "Where do orders come from?", "Orders of the top 6 states",
                  bars("State Orders Leader Colour"), topn(G, "State", "Orders", 6), sort_by(mea("Orders")))]),
    "pg02Sales": dict(
        kpis=[("Revenue Growth %", "Revenue LY Text"), vsly("Items Sold"), vsly("Average Item Price"), vsly("Freight % of Revenue"), vsly("Revenue per Customer")],
        charts=[
            chart("lineStackedColumnComboChart", roles(Category=col(D, "Month"), Y=mea("Revenue"), Y2=mea("Revenue LY")), "Revenue by month, this year against last",
                  "Columns of revenue by month with last year as a line",
                  {**axis_small(), "legend": [{"properties": {"show": lit("true"), "position": lit("'Top'"), "fontSize": lit("9D")}}],
                   "labels": [{"properties": {"show": lit("false")}}],
                   "valueAxis": [{"properties": {"show": lit("true"), "fontSize": lit("9D"), "gridlineShow": lit("true")}}],
                   "dataPoint": [dp_series("Revenue", ACCENT), dp_series("Revenue LY", "#C9D3DC")],
                   "lineStyles": [{"properties": {"lineStyle": lit("'dashed'")}, "selector": {"metadata": "_Measures.Revenue LY"}}]}),
            chart("clusteredColumnChart", roles(Category=col(D, "Weekday"), Y=mea("Revenue")), "Which weekday sells most?", "Revenue by weekday",
                  {**axis_small(), "dataPoint": [dp_measure("Weekday Leader Colour")]}),
            chart("treemap", roles(Group=col(G, "Region"), Details=col(G, "State"), Values=mea("Revenue")), "Which states sell most?", "Treemap of revenue by region and state",
                  with_legend({})),
            chart("waterfallChart", roles(Category=col(G, "Region"), Y=mea("Revenue Change vs LY")), "Which regions drive growth against last year?",
                  "Waterfall of the revenue change against last year by region",
                  {**labels_on({}), "legend": [{"properties": {"show": lit("false")}}],
                   "sentimentColors": [{"properties": {"increaseFill": solid(GOOD), "decreaseFill": solid(BAD), "totalFill": solid(ACCENT)}}]})]),
    "pg03Products": dict(
        kpis=[("Revenue", "Revenue vs LY %"), vsly("Items Sold"), vsly("Categories With Sales"), vsly("Average Item Price"), ("Top Category Share", "Top Category Text")],
        charts=[
            chart("clusteredBarChart", roles(Category=col(P, "Category"), Y=mea("Revenue")), "Which categories sell most?", "Revenue of the top 5 categories",
                  bars("Category Leader Colour"), topn(P, "Category", "Revenue", 5), sort_by(mea("Revenue"))),
            chart("lineChart", roles(Category=col(D, "Month Start"), Y=mea("Revenue")), "Is the selected category growing?", "Revenue by month for the selected categories, with a trend line",
                  trend(straight(axis_small()))),
            chart("clusteredColumnChart", roles(Category=col(PB, "Price Band"), Y=mea("Items Sold")), "Which price band sells most?", "Items sold by price band",
                  {**axis_small(), "dataPoint": [dp_measure("Price Band Leader Colour")]}),
            table([col(P, "Category"), mea("Revenue"), mea("Items Sold"), mea("Average Item Price"), mea("Average Review")], "Category detail", "Table of categories", "Revenue", widths=(150, 85, 85, 105, 105))]),
    "pg04Customers": dict(
        kpis=[vsly("Customers"), vsly("New Customers"), ("Repeat Customers %", "Returning Customers Text"), vsly("Orders per Customer"), vsly("Revenue per Customer")],
        charts=[
            chart("stackedAreaChart", roles(Category=col(D, "Month Start"), Y=[mea("New Orders"), mea("Returning Orders")]), "New and returning orders by month",
                  "Stacked area of new and returning orders by month",
                  with_legend({**axis_small(), "dataPoint": [dp_series("New Orders", ACCENT), dp_series("Returning Orders", "#E14E3A")]})),
            {"visual": {"visualType": "map", "query": roles(Category=col(G, "City"), X=mea("City Longitude"), Y=mea("City Latitude"), Size=mea("Customers")),
                        "objects": {}, "visualContainerObjects": container("Where do customers live?", "Map of the 500 cities with most customers"), "drillFilterOtherVisuals": True},
             "filterConfig": topn(G, "City", "Customers", 500)},
            chart("pieChart", roles(Category=col(CU, "Customer Type"), Y=mea("Customers")), "Do customers come back?", "Pie of customers with a repeat order against one-time customers",
                  {**with_legend({}, "Right"), **labels_on({}), "dataPoint": [dp_member(CU, "Customer Type", "Repeat", ACCENT), dp_member(CU, "Customer Type", "One-time", "#C9D3DC")]}),
            chart("clusteredBarChart", roles(Category=col(G, "City"), Y=mea("Customers")), "Which cities have most customers?", "Customers of the top 6 cities",
                  bars("City Leader Colour"), topn(G, "City", "Customers", 6), sort_by(mea("Customers")))]),
    "pg05Delivery": dict(
        kpis=[vsly("Late Deliveries %"), vsly("Average Delivery Days"), vsly("Average Days Late"), vsly("Late Orders"), vsly("Cancellation %")],
        charts=[
            chart("lineChart", roles(Category=col(D, "Month Start"), Y=mea("Late Deliveries %")), "Are late deliveries falling?", "Late deliveries by month",
                  {**straight(axis_small()), "dataPoint": [dp_series("Late Deliveries %", BAD)]}),
            chart("pieChart", roles(Category=col(ST_, "Delivery Status"), Y=mea("Orders")), "How many orders arrive late?", "Pie of orders on time against late",
                  {**with_legend({}, "Right"), **labels_on({}), "dataPoint": [dp_member(ST_, "Delivery Status", "On time", GOOD), dp_member(ST_, "Delivery Status", "Late", BAD),
                                                                             dp_member(ST_, "Delivery Status", "No date", NEUTRAL), dp_member(ST_, "Delivery Status", "Not delivered", NEUTRAL)]}),
            chart("scatterChart", roles(Category=col(G, "State"), X=mea("Average Delivery Days"), Y=mea("Late Deliveries %"), Size=mea("Delivered Orders")),
                  "Which states are slow and unreliable?", "Scatter of delivery days against late deliveries by state; red marks states worse than overall on both",
                  {"categoryAxis": [{"properties": {"fontSize": lit("9D")}}], "legend": [{"properties": {"show": lit("false")}}], "dataPoint": [dp_measure("State Delivery Colour")]}),
            chart("clusteredBarChart", roles(Category=col(G, "State"), Y=mea("Late Deliveries %")), "Which states are late most often? (200+ orders)",
                  "Late deliveries of the 6 worst states with 200 delivered orders or more; red is above the overall rate",
                  bars("Late State Colour"), topn(G, "State", "Late Rank Helper", 6), sort_by(mea("Late Deliveries %")))]),
    "pg06Reviews": dict(
        kpis=[vsly("Average Review"), vsly("One Star %"), vsly("Five Star %"), vsly("Review Rate %"), ("Average Review Late", "Review Gap Late vs On Time")],
        charts=[
            chart("clusteredColumnChart", roles(Category=col("Sales", "Review Score"), Y=mea("Reviewed Orders")), "How do customers score us?", "Reviewed orders by score; scores 1 and 2 red, 3 grey, 4 and 5 green",
                  {**axis_small(), "dataPoint": [dp_measure("Score Class Colour")]}),
            chart("lineChart", roles(Category=col(D, "Month Start"), Y=mea("Average Review")), "Is the score improving?", "Average review by month, with a trend line", trend(straight(axis_small()))),
            chart("clusteredBarChart", roles(Category=col(P, "Category"), Y=mea("Average Review")), "Which categories score lowest?", "Average review of the 6 lowest categories with 200 orders or more",
                  {**axis_small(), "categoryAxis": [{"properties": {"fontSize": lit("9D"), "maxMarginFactor": lit("45L")}}], "dataPoint": [{"properties": {"fill": solid(BAD)}}]},
                  topn(P, "Category", "Review Rank Helper", 6, 1), sort_by(mea("Average Review"), "Ascending")),
            chart("gauge", roles(Y=mea("Average Review Late"), TargetValue=mea("Average Review On Time")), "What does a late order cost in score?",
                  "Gauge of the average review of late orders against the on-time average as target",
                  {"axis": [{"properties": {"min": lit("1D"), "max": lit("5D")}}],
                   "dataPoint": [{"properties": {"fill": solid(BAD), "target": solid(NEUTRAL)}}],
                   "calloutValue": [{"properties": {"show": lit("true")}}]})]),
    "pg07Sellers": dict(
        kpis=[vsly("Active Sellers"), vsly("Revenue per Seller"), vsly("Late Deliveries %"), vsly("Average Review"), vsly("Freight % of Revenue")],
        charts=[
            chart("clusteredBarChart", roles(Category=col(S_, "Seller"), Y=mea("Revenue")), "Who sells most?", "Revenue of the top 5 sellers", bars("Seller Leader Colour"),
                  topn(S_, "Seller", "Revenue", 5), sort_by(mea("Revenue"))),
            chart("treemap", roles(Group=col(S_, "Seller State"), Values=mea("Active Sellers")), "Where are the sellers?", "Treemap of active sellers by state", {"legend": [{"properties": {"show": lit("false")}}]}),
            chart("scatterChart", roles(Category=col(S_, "Seller"), X=mea("Late Deliveries %"), Y=mea("Average Review"), Size=mea("Revenue")), "Do late sellers get lower scores? (top 100 by revenue)",
                  "Scatter of late deliveries against average review for the 100 sellers with most revenue; red marks sellers later and lower-rated than overall",
                  {"categoryAxis": [{"properties": {"fontSize": lit("9D")}}], "legend": [{"properties": {"show": lit("false")}}], "dataPoint": [dp_measure("Seller Risk Colour")]},
                  topn(S_, "Seller", "Revenue", 100)),
            table([col(S_, "Seller"), col(S_, "Seller State"), mea("Revenue"), mea("Orders"), mea("Late Deliveries %"), mea("Average Review")], "Seller detail", "Table of sellers", "Revenue", widths=(105, 85, 80, 65, 110, 100))]),
    "pg08DataTable": dict(
        kpis=[("Revenue", "Revenue vs LY %"), vsly("Orders"), vsly("Late Deliveries %"), vsly("Average Review")],
        charts=[table([col(D, "Year Month"), col(G, "State"), mea("Revenue"), mea("Orders"), mea("Late Deliveries %"), mea("Average Review")], "Month and state",
                      "Table of revenue, orders, late deliveries and review by month and state", "Revenue", total=True, padding=8, widths=(170, 150, 230, 210, 230, 200))]),
}


def place(v, rect, z, inset=INSET, right_pad=0):
    x, y, w, h = rect
    v["position"] = {"x": x + inset, "y": y + inset, "z": z, "width": w - 2 * inset - right_pad, "height": h - 2 * inset, "tabOrder": z}
    return v


def write(pid, name, v):
    v["$schema"] = SCHEMA
    v["name"] = name
    d = REPORT / "pages" / pid / "visuals" / name
    d.mkdir(parents=True, exist_ok=True)
    order = ["$schema", "name", "position", "visual", "filterConfig"]
    (d / "visual.json").write_text(json.dumps({k: v[k] for k in order if k in v}, indent=2, ensure_ascii=False), encoding="utf-8")


n = 0
for pid, spec in PAGES.items():
    vis = REPORT / "pages" / pid / "visuals"
    for old in vis.glob("*"):
        if old.name.startswith(("kpi", "chart", "slicer")):
            shutil.rmtree(old)
    lay = LAYOUT["pages"][pid]
    assert len(spec["kpis"]) == len(lay["kpis"]), pid
    assert len(spec["charts"]) == len(lay["cards"]), pid
    for i, (m_, ref) in enumerate(spec["kpis"]):
        write(pid, "kpi%02d%s" % (i + 1, m_.replace(" ", "").replace("%", "Pct")[:28]),
              place(kpi(m_, ref, "%s, compared with last year" % m_, millions=(m_ == "Revenue")), lay["kpis"][i], 1000 + i, inset=2, right_pad=44))
        n += 1
    for i, c in enumerate(spec["charts"]):
        write(pid, "chart%02d" % (i + 1), place(c, lay["cards"][i], 2000 + i))
        n += 1
    sl = lay["slicers"]
    write(pid, "slicerYear", place(slicer(YEAR, "Year", "Year", default="2018L", single=True), sl[0], 600, inset=0))
    write(pid, "slicerState", place(slicer(STATE, "State", "State"), sl[1], 601, inset=0))
    n += 2
print("visuals written:", n, "on", len(PAGES), "pages")
