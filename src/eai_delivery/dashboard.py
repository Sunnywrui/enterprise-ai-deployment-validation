from __future__ import annotations
from pathlib import Path
import json, html

def build_dashboard_data(out_dir, revalidation_plan=None):
    out = Path(out_dir)
    ref = json.loads((out/"reference_metrics.json").read_text())
    tgt = json.loads((out/"target_metrics.json").read_text())
    delta = json.loads((out/"deployment_delta.json").read_text())
    decision = delta["decision"]
    return {
        "overall_verdict": decision["overall_verdict"],
        "mandatory_failures": decision["mandatory_metric_failures"],
        "reference": ref,
        "target": tgt,
        "delta_metrics": delta["metrics"],
        "revalidation": revalidation_plan or {},
        "release_ready": decision["mandatory_metric_failures"] == 0
    }

def write_html_dashboard(path, data):
    verdict = data["overall_verdict"]
    status_class = "pass" if verdict.startswith("PASS") else "fail"
    rows = []
    for r in data["delta_metrics"]:
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(r['metric']))}</td>"
            f"<td>{r.get('reference')}</td><td>{r.get('target')}</td><td>{r.get('delta')}</td>"
            f"<td>{html.escape(str(r.get('threshold_type')))} {r.get('threshold')}</td>"
            f"<td class='{str(r.get('verdict','')).lower()}'>{r.get('verdict')}</td>"
            "</tr>"
        )
    rv = data.get("revalidation", {})
    changes = "".join(f"<li>{html.escape(str(x))}</li>" for x in rv.get("required_revalidation", [])) or "<li>None</li>"
    doc = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Enterprise AI Release Readiness</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 32px; color: #172033; background: #f6f8fb; }}
h1 {{ margin-bottom: 4px; }} .sub {{ color: #657086; margin-bottom: 24px; }}
.cards {{ display:flex; gap:16px; flex-wrap:wrap; margin-bottom:24px; }}
.card {{ background:white; border:1px solid #dce2ea; border-radius:10px; padding:18px; min-width:190px; box-shadow:0 2px 8px #0000000b; }}
.big {{ font-size:28px; font-weight:700; }} .pass {{ color:#137333; }} .fail {{ color:#b3261e; }}
table {{ border-collapse:collapse; width:100%; background:white; }}
th,td {{ border:1px solid #dce2ea; padding:9px; text-align:left; }}
th {{ background:#eaf0f8; }} td.pass {{ font-weight:700; color:#137333; }} td.fail {{ font-weight:700; color:#b3261e; }}
section {{ margin-top:26px; }}
</style>
</head>
<body>
<h1>Enterprise AI Release Readiness</h1>
<div class="sub">Deployment Contract → Behavioral Equivalence → Evidence → Release Gate</div>
<div class="cards">
<div class="card"><div>Overall Verdict</div><div class="big {status_class}">{html.escape(verdict)}</div></div>
<div class="card"><div>Mandatory Failures</div><div class="big">{data['mandatory_failures']}</div></div>
<div class="card"><div>Target Case Runs</div><div class="big">{data['target'].get('case_runs')}</div></div>
<div class="card"><div>Cost / Accepted Workflow</div><div class="big">{data['target'].get('cost_per_accepted_workflow')}</div></div>
</div>
<section>
<h2>Behavioral Equivalence Gates</h2>
<table>
<thead><tr><th>Metric</th><th>Reference</th><th>Target</th><th>Delta</th><th>Gate</th><th>Verdict</th></tr></thead>
<tbody>{''.join(rows)}</tbody>
</table>
</section>
<section>
<h2>Contract Change Revalidation</h2>
<p>Risk: <strong>{html.escape(str(rv.get('risk_level','N/A')))}</strong> · Material changes: <strong>{rv.get('material_change_count',0)}</strong></p>
<ul>{changes}</ul>
</section>
</body></html>"""
    Path(path).write_text(doc, encoding="utf-8")
