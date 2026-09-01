from __future__ import annotations
from pathlib import Path
import json, shutil
from .config import load_yaml
from .revalidation import generate_revalidation_plan, render_markdown
from .runner import compare_profiles
from .dashboard import build_dashboard_data, write_html_dashboard
from .evidence import create_evidence_bundle

def _copy(src, dst_dir, name):
    if not src:
        return
    p = Path(src)
    if p.exists():
        shutil.copy2(p, Path(dst_dir)/name)

def run_release_gate(reference_contract, target_contract, reference_profile, target_profile,
                     golden, thresholds, out_dir, evidence_bundle=None,
                     human_reviews=None, judge_profile=None):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    ref_contract = load_yaml(reference_contract)
    tgt_contract = load_yaml(target_contract)
    plan = generate_revalidation_plan(ref_contract, tgt_contract)
    (out/"revalidation_plan.md").write_text(render_markdown(plan), encoding="utf-8")

    _copy(reference_contract, out, "reference_contract.yaml")
    _copy(target_contract, out, "target_contract.yaml")
    _copy(golden, out, "golden_cases.csv")
    _copy(thresholds, out, "thresholds.yaml")
    if human_reviews:
        _copy(human_reviews, out, "human_reviews.csv")

    decision = compare_profiles(
        reference_profile, target_profile, golden, thresholds, out,
        judge_profile, human_reviews
    )

    dashboard = build_dashboard_data(out, plan)
    (out/"dashboard_data.json").write_text(
        json.dumps(dashboard, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_html_dashboard(out/"release_dashboard.html", dashboard)

    if evidence_bundle:
        create_evidence_bundle(
            out, evidence_bundle,
            metadata={
                "reference_deployment": reference_profile.get("deployment_id"),
                "target_deployment": target_profile.get("deployment_id"),
                "release_verdict": decision["overall_verdict"],
                "material_change_count": plan["material_change_count"],
                "risk_level": plan["risk_level"],
            }
        )
    return decision, plan, dashboard
