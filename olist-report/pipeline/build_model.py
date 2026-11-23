"""Write the semantic model of the Olist report as TMDL (definition/ folder), from the tables made by build_star.py.

usage: python pipeline/build_model.py

Same inputs, same files (lineage tags are derived from the object names). Writes expressions.tmdl, relationships.tmdl,
tables/*.tmdl and the ref lines of model.tmdl. Measures live in pipeline/measures.py.
"""
import re
import uuid
from pathlib import Path

import pandas as pd

from measures import MEASURES, delta_measures

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DEF = ROOT / "olist_e_commerce_report.SemanticModel" / "definition"
(DEF / "tables").mkdir(exist_ok=True)


def tag(*parts):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "olist/" + "/".join(parts)))


def q(name):  # TMDL name quoting
    return "'%s'" % name.replace("'", "''") if re.search(r"[^A-Za-z0-9_]", name) or name[0].isdigit() else name


# column: name -> (dataType, M type, extras). extras: hidden, fmt, folder, sort, cat, key
S, I, D, DEC, F = "string", "int64", "dateTime", "decimal", "double"
M_TYPE = {S: "type text", I: "Int64.Type", D: "type date", DEC: "Currency.Type", F: "type number"}
DATE_FMT = "yyyy-mm-dd"

TABLES = {
    "Date": dict(file="Date.csv", category="Time", cols=[
        ("Date", D, dict(key=True, fmt=DATE_FMT)), ("Year", I, {}), ("Quarter", S, {}), ("Month Number", I, dict(hidden=True)),
        ("Month", S, dict(sort="Month Number")), ("Year Month", S, {}), ("Weekday Number", I, dict(hidden=True)),
        ("Weekday", S, dict(sort="Weekday Number")), ("Month Start", D, dict(fmt="mmm yyyy")),
        ("Quarter Label", S, dict(sort="Year Quarter")), ("Year Quarter", I, dict(hidden=True))]),
    "Customer": dict(file="Customer.csv", cols=[("Customer Key", S, dict(hidden=True)), ("Customer Type", S, {})]),
    "Geography": dict(file="Geography.csv", hierarchy=("Geography", ["Region", "State", "City"]), cols=[
        ("Geography Key", S, dict(hidden=True)), ("City", S, {}), ("State", S, {}), ("Region", S, {}),
        ("Latitude", F, dict(cat="Latitude", fmt="0.0000")), ("Longitude", F, dict(cat="Longitude", fmt="0.0000"))]),
    "Product": dict(file="Product.csv", cols=[("Product Key", S, dict(hidden=True)), ("Category", S, {})]),
    "Seller": dict(file="Seller.csv", cols=[("Seller Key", S, dict(hidden=True)), ("Seller", S, {}), ("Seller City", S, {}), ("Seller State", S, {})]),
    "Order Status": dict(file="Order Status.csv", cols=[("Order Status Key", S, dict(hidden=True)), ("Order Status", S, {}), ("Delivery Status", S, {})]),
    "Price Band": dict(file="Price Band.csv", cols=[("Price Band Key", S, dict(hidden=True)), ("Price Band", S, dict(sort="Band Order")), ("Band Order", I, dict(hidden=True))]),
    "Payment Type": dict(file="Payment Type.csv", cols=[("Payment Type Key", S, dict(hidden=True)), ("Payment Type", S, {})]),
    "Sales": dict(file="Sales.csv", cols=[
        ("Order Id", S, dict(hidden=True)), ("Order Line", I, dict(hidden=True)), ("Purchase Date", D, dict(hidden=True, fmt=DATE_FMT)),
        ("Customer Key", S, dict(hidden=True)), ("Geography Key", S, dict(hidden=True)), ("Product Key", S, dict(hidden=True)),
        ("Seller Key", S, dict(hidden=True)), ("Order Status Key", S, dict(hidden=True)), ("Price Band Key", S, dict(hidden=True)),
        ("Price", DEC, dict(hidden=True, fmt="#,##0.00")), ("Freight", DEC, dict(hidden=True, fmt="#,##0.00")),
        ("Review Score", I, dict(hidden=True)), ("Delivery Days", I, dict(hidden=True)), ("Days Late", I, dict(hidden=True)),
        ("Is First Order", I, dict(hidden=True))]),
    "Payments": dict(file="Payments.csv", cols=[
        ("Order Id", S, dict(hidden=True)), ("Payment Sequence", I, dict(hidden=True)), ("Purchase Date", D, dict(hidden=True, fmt=DATE_FMT)),
        ("Customer Key", S, dict(hidden=True)), ("Geography Key", S, dict(hidden=True)), ("Order Status Key", S, dict(hidden=True)),
        ("Payment Type Key", S, dict(hidden=True)), ("Installments", I, dict(hidden=True)),
        ("Payment Value", DEC, dict(hidden=True, fmt="#,##0.00"))]),
}

RELATIONSHIPS = [  # fact column -> dimension column; many to one, single direction, active
    ("Sales", "Purchase Date", "Date", "Date"), ("Sales", "Customer Key", "Customer", "Customer Key"),
    ("Sales", "Geography Key", "Geography", "Geography Key"), ("Sales", "Product Key", "Product", "Product Key"),
    ("Sales", "Seller Key", "Seller", "Seller Key"), ("Sales", "Order Status Key", "Order Status", "Order Status Key"),
    ("Sales", "Price Band Key", "Price Band", "Price Band Key"),
    ("Payments", "Purchase Date", "Date", "Date"), ("Payments", "Customer Key", "Customer", "Customer Key"),
    ("Payments", "Geography Key", "Geography", "Geography Key"), ("Payments", "Order Status Key", "Order Status", "Order Status Key"),
    ("Payments", "Payment Type Key", "Payment Type", "Payment Type Key"),
]

# the columns of every CSV must match the table definition: stop here, not in Desktop
for name, t in TABLES.items():
    head = list(pd.read_csv(DATA / t["file"], nrows=0).columns)
    assert head == [c[0] for c in t["cols"]], f"{name}: CSV columns {head}"


def column_block(table, name, dtype, x):
    out = ["\tcolumn %s" % q(name), "\t\tdataType: %s" % dtype]
    if x.get("fmt"):
        out.append("\t\tformatString: %s" % x["fmt"])
    if x.get("hidden"):
        out.append("\t\tisHidden")
    if x.get("key"):
        out.append("\t\tisKey")
    if x.get("cat"):
        out.append("\t\tdataCategory: %s" % x["cat"])
    out.append("\t\tlineageTag: %s" % tag(table, name))
    out.append("\t\tsummarizeBy: none")
    out.append("\t\tsourceColumn: %s" % name)
    if x.get("sort"):
        out.append("\t\tsortByColumn: %s" % q(x["sort"]))
    out += ["", "\t\tannotation SummarizationSetBy = Automatic", ""]
    return "\n".join(out)


def partition_m(table, t):
    types = ", ".join('{"%s", %s}' % (c[0], M_TYPE[c[1]]) for c in t["cols"])
    lines = [
        "let",
        '    Source = Csv.Document(File.Contents(#"Data Folder" & "\\%s"), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),' % t["file"],
        "    #\"Promoted Headers\" = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),",
        '    #"Changed Types" = Table.TransformColumnTypes(#"Promoted Headers", {%s}, "en-US")' % types,
        "in",
        '    #"Changed Types"']
    return "\n".join("\t\t\t\t" + l for l in lines)


def write(path, text):
    Path(path).write_text(text, encoding="utf-8", newline="\n")


for name, t in TABLES.items():
    parts = ["table %s" % q(name), "\tlineageTag: %s" % tag(name)]
    if t.get("category"):
        parts.append("\tdataCategory: %s" % t["category"])
    parts.append("")
    for c in t["cols"]:
        parts.append(column_block(name, *c))
    if t.get("hierarchy"):
        hn, levels = t["hierarchy"]
        parts.append("\thierarchy %s" % q(hn))
        parts.append("\t\tlineageTag: %s\n" % tag(name, hn))
        for lv in levels:
            parts.append("\t\tlevel %s\n\t\t\tlineageTag: %s\n\t\t\tcolumn: %s\n" % (q(lv), tag(name, hn, lv), q(lv)))
    parts.append("\tpartition %s = m\n\t\tmode: import\n\t\tsource =\n%s\n" % (q(name), partition_m(name, t)))
    parts.append("\tannotation PBI_ResultType = Table\n")
    write(DEF / "tables" / f"{name}.tmdl", "\n".join(parts))

# ---------------------------------------------------------------- measures table
allm = MEASURES + delta_measures()
names = [m["name"] for m in allm]
assert len(names) == len(set(names)), "duplicate measure name"
mt = ["table _Measures", "\tlineageTag: %s" % tag("_Measures"), ""]
for m in allm:
    dax = m["dax"].strip("\n")
    body = "\n".join("\t\t\t" + l for l in dax.split("\n"))
    mt.append("\t/// %s" % m["desc"])
    mt.append("\tmeasure %s =\n%s" % (q(m["name"]), body))
    if m.get("fmt"):
        mt.append("\t\tformatString: %s" % m["fmt"])
    if m.get("hidden"):
        mt.append("\t\tisHidden")
    mt.append("\t\tdisplayFolder: %s" % m["folder"])
    mt.append("\t\tlineageTag: %s\n" % tag("_Measures", m["name"]))
mt.append("\tcolumn Value\n\t\tisHidden\n\t\tdataType: int64\n\t\tlineageTag: %s\n\t\tsummarizeBy: none\n\t\tisNameInferred\n\t\tsourceColumn: [Value]\n\n"
          "\t\tannotation SummarizationSetBy = Automatic\n" % tag("_Measures", "Value"))
mt.append("\tpartition _Measures = calculated\n\t\tmode: import\n\t\tsource = {1}\n")
write(DEF / "tables" / "_Measures.tmdl", "\n".join(mt))

# ---------------------------------------------------------------- relationships, expressions, model
rel = []
for f_t, f_c, t_t, t_c in RELATIONSHIPS:
    rel.append("relationship %s\n\tfromColumn: %s.%s\n\ttoColumn: %s.%s\n" % (tag("rel", f_t, f_c, t_t), q(f_t), q(f_c), q(t_t), q(t_c)))
write(DEF / "relationships.tmdl", "\n".join(rel))

folder = str(DATA).replace("/", "\\")
write(DEF / "expressions.tmdl",
      'expression \'Data Folder\' = "%s" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]\n'
      "\tlineageTag: %s\n\n\tannotation PBI_ResultType = Text\n" % (folder, tag("Data Folder")))

model = (DEF / "model.tmdl").read_text(encoding="utf-8")
model = re.sub(r"^ref (?:table|expression) .*\n", "", model, flags=re.M)
model = model.replace("__PBI_TimeIntelligenceEnabled = 1", "__PBI_TimeIntelligenceEnabled = 0")
refs = "".join("ref table %s\n" % q(n) for n in list(TABLES) + ["_Measures"])
model = model.replace("ref cultureInfo en-US", refs + "ref expression 'Data Folder'\nref cultureInfo en-US")
write(DEF / "model.tmdl", model)
print("tables:", len(TABLES) + 1, "| relationships:", len(RELATIONSHIPS), "| measures:", len(allm))
