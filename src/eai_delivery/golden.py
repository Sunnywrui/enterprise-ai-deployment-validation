from __future__ import annotations
import csv, json
from pathlib import Path

def _b(v):
    return str(v).strip().lower() in {"1","yes","true","y"}

def load_golden_csv(path):
    cases = []
    with Path(path).open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            c = {k.strip().lower(): (v or "").strip() for k,v in row.items()}
            c["case_id"] = c.pop("case_id")
            c["weight"] = float(c.get("weight") or 1)
            c["mandatory"] = _b(c.get("mandatory", "yes"))
            c["expected_arguments"] = json.loads(c["expected_arguments_json"]) if c.get("expected_arguments_json") else None
            cases.append(c)
    return cases
