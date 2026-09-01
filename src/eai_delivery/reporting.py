from __future__ import annotations
from pathlib import Path
import csv, json
from dataclasses import asdict

def write_case_results(path, results):
    rows = [asdict(r) for r in results]
    if not rows: return
    with Path(path).open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)

def write_json(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def write_delta_csv(path, rows):
    if not rows: return
    with Path(path).open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)

def write_release_md(path, decision, rows, ref_id, target_id):
    lines = [
        "# Enterprise AI Deployment Release Decision",
        "",
        f"- Reference: `{ref_id}`",
        f"- Target: `{target_id}`",
        f"- Overall verdict: **{decision['overall_verdict']}**",
        f"- Mandatory metric failures: **{decision['mandatory_metric_failures']}**",
        "",
        "## Metric gates",
        "",
        "| Metric | Reference | Target | Delta | Gate | Mandatory | Verdict |",
        "|---|---:|---:|---:|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['metric']} | {r['reference']} | {r['target']} | {r['delta']} | "
            f"{r['threshold_type']} {r['threshold']} | {r['mandatory']} | **{r['verdict']}** |"
        )
    lines += [
        "",
        "## Release rule",
        "",
        "Any mandatory FAIL or INCONCLUSIVE blocks automatic release. Residual risk requires explicit owner acceptance and compensating controls.",
    ]
    Path(path).write_text("\n".join(lines), encoding="utf-8")
