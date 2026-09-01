import argparse, json
from pathlib import Path
from .config import load_yaml, load_profile, validate_contract
from .contract_diff import diff_contracts
from .runner import compare_profiles
from .revalidation import generate_revalidation_plan, render_markdown
from .release_gate import run_release_gate
from .evidence import verify_evidence_bundle
from .drift import load_observations, summarize_observations

DEFAULT_SCHEMA = str(Path(__file__).resolve().parents[3] / "examples" / "deployment_contract.schema.json")

def main():
    p = argparse.ArgumentParser(prog="eai-delivery")
    sub = p.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("validate-contract")
    v.add_argument("contract")
    v.add_argument("--schema", default=DEFAULT_SCHEMA)

    d = sub.add_parser("diff-contracts")
    d.add_argument("reference")
    d.add_argument("target")

    rp = sub.add_parser("revalidation-plan")
    rp.add_argument("reference")
    rp.add_argument("target")
    rp.add_argument("--out")

    c = sub.add_parser("compare")
    c.add_argument("--reference-profile", required=True)
    c.add_argument("--target-profile", required=True)
    c.add_argument("--golden", required=True)
    c.add_argument("--thresholds", required=True)
    c.add_argument("--out", default="out")
    c.add_argument("--judge-profile")
    c.add_argument("--human-reviews")

    g = sub.add_parser("release-gate")
    g.add_argument("--reference-contract", required=True)
    g.add_argument("--target-contract", required=True)
    g.add_argument("--reference-profile", required=True)
    g.add_argument("--target-profile", required=True)
    g.add_argument("--golden", required=True)
    g.add_argument("--thresholds", required=True)
    g.add_argument("--human-reviews")
    g.add_argument("--judge-profile")
    g.add_argument("--out", default="out")
    g.add_argument("--evidence-bundle")

    ev = sub.add_parser("verify-evidence")
    ev.add_argument("bundle")

    dr = sub.add_parser("summarize-drift")
    dr.add_argument("observations")

    a = p.parse_args()

    if a.cmd == "validate-contract":
        _, errs = validate_contract(a.contract, a.schema)
        if errs:
            for e in errs:
                print(f"FAIL {'/'.join(map(str,e.path))}: {e.message}")
            raise SystemExit(2)
        print("PASS contract schema validation")

    elif a.cmd == "diff-contracts":
        ch = diff_contracts(load_yaml(a.reference), load_yaml(a.target))
        print(json.dumps(ch, ensure_ascii=False, indent=2))
        raise SystemExit(1 if ch else 0)

    elif a.cmd == "revalidation-plan":
        md = render_markdown(generate_revalidation_plan(load_yaml(a.reference), load_yaml(a.target)))
        if a.out:
            Path(a.out).write_text(md, encoding="utf-8")
        print(md)

    elif a.cmd == "compare":
        judge = load_profile(a.judge_profile) if a.judge_profile else None
        decision = compare_profiles(
            load_profile(a.reference_profile), load_profile(a.target_profile),
            a.golden, a.thresholds, a.out, judge, a.human_reviews
        )
        print(json.dumps(decision, indent=2))
        raise SystemExit(2 if decision["overall_verdict"] == "FAIL" else 0)

    elif a.cmd == "release-gate":
        judge = load_profile(a.judge_profile) if a.judge_profile else None
        decision, plan, dashboard = run_release_gate(
            a.reference_contract, a.target_contract,
            load_profile(a.reference_profile), load_profile(a.target_profile),
            a.golden, a.thresholds, a.out, a.evidence_bundle,
            a.human_reviews, judge
        )
        print(json.dumps({
            "decision": decision,
            "material_changes": plan["material_change_count"],
            "risk_level": plan["risk_level"],
            "release_ready": dashboard["release_ready"]
        }, indent=2))
        raise SystemExit(2 if decision["overall_verdict"] == "FAIL" else 0)

    elif a.cmd == "verify-evidence":
        result = verify_evidence_bundle(a.bundle)
        print(json.dumps(result, indent=2))
        raise SystemExit(0 if result["valid"] else 2)

    elif a.cmd == "summarize-drift":
        print(json.dumps(summarize_observations(load_observations(a.observations)), indent=2))

if __name__ == "__main__":
    main()
