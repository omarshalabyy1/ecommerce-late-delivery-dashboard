"""After make_frames.py: make the top-navigation labels fit. The button text ("Customers") is cut at 10 pt with a 30 px left margin;
this sets 9 pt and a 27 px margin on every ff_nav* button. Deterministic; rerun after every make_frames.py run.
make_frames.py belongs to the powerbi-kit hub, so its output is adjusted here, not in the hub script."""
import glob
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
n = 0
for f in sorted(glob.glob(str(ROOT / "olist_e_commerce_report.Report/definition/pages/*/visuals/ff_nav*/visual.json"))):
    v = json.load(open(f, encoding="utf-8"))
    text = v["visual"]["objects"].get("text", [])
    for block in text:
        pr = block.get("properties", {})
        if "fontSize" in pr:
            pr["fontSize"] = {"expr": {"Literal": {"Value": "9D"}}}
            pr["leftMargin"] = {"expr": {"Literal": {"Value": "27L"}}}
            n += 1
    Path(f).write_text(json.dumps(v, indent=2, ensure_ascii=False), encoding="utf-8")
print("nav buttons adjusted:", n)
