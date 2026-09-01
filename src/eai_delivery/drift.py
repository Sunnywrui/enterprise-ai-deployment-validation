from __future__ import annotations
import csv
from pathlib import Path

def load_observations(path):
    with Path(path).open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def summarize_observations(rows):
    total = len(rows)
    if not total:
        return {"observations": 0}
    accepted = sum(str(r.get("human_accepted","")).lower() in {"1","true","yes","y"} for r in rows)
    failures = sum(str(r.get("workflow_failed","")).lower() in {"1","true","yes","y"} for r in rows)
    lat = [float(r["latency_ms"]) for r in rows if r.get("latency_ms")]
    costs = [float(r["total_workflow_cost_usd"]) for r in rows if r.get("total_workflow_cost_usd")]
    return {
        "observations": total,
        "human_acceptance_rate": accepted/total,
        "workflow_failure_rate": failures/total,
        "avg_latency_ms": sum(lat)/len(lat) if lat else None,
        "avg_workflow_cost_usd": sum(costs)/len(costs) if costs else None
    }
