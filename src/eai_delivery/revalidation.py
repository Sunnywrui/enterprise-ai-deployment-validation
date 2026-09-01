from collections import defaultdict
from .contract_diff import diff_contracts

def generate_revalidation_plan(reference,target):
    changes=diff_contracts(reference,target); grouped=defaultdict(list)
    for c in changes: grouped[c["domain"]].append(c)
    tests=[]
    if any(d in grouped for d in ["model","artifact"]): tests += ["Golden critical-path regression","Task quality","Tool calling","Structured output","Workflow economics"]
    if "protocol" in grouped: tests += ["Full affected tool/structured-output suite","Tool argument JSON Schema validation","Permission boundary tests"]
    if any(d in grouped for d in ["runtime","hardware"]): tests += ["P50/P95 latency","Throughput","Critical accuracy/tool regression","Capacity/soak test"]
    if "enterprise" in grouped: tests += ["Affected RAG workflows","Guardrail/authZ regression","Data/permission compliance"]
    if "inference" in grouped: tests += ["Repeated stochastic trials","Confidence interval review","Latency/cost regression"]
    if "business" in grouped: tests += ["Business-owner re-acceptance","Threshold/risk-class review","Failure-loss/economics review"]
    tests=list(dict.fromkeys(tests)); risk="LOW"
    if grouped:risk="MEDIUM"
    if any(d in grouped for d in ["model","artifact","protocol","business"]):risk="HIGH"
    return {"material_change_count":len(changes),"risk_level":risk,"changed_domains":sorted(grouped),
            "changes":changes,"required_revalidation":tests,"automatic_release_allowed":not bool(changes),
            "approval_required":["FDE/AI Architect","QA/Evaluation"]+(["Business/Risk Owner"] if risk=="HIGH" else [])}

def render_markdown(plan):
    lines=["# Contract Change Revalidation Plan","",f"- Material changes: **{plan['material_change_count']}**",
           f"- Risk level: **{plan['risk_level']}**",f"- Automatic release allowed: **{plan['automatic_release_allowed']}**",
           "","## Changed domains"]+[f"- {x}" for x in plan["changed_domains"]]
    lines += ["","## Required revalidation"]+[f"- {x}" for x in plan["required_revalidation"]]
    lines += ["","## Approvals"]+[f"- {x}" for x in plan["approval_required"]]
    lines += ["","## Detailed contract changes","","| Domain | Field | Reference | Target | Revalidation |","|---|---|---|---|---|"]
    for c in plan["changes"]:
        lines.append(f"| {c['domain']} | `{c['field']}` | `{c['reference']}` | `{c['target']}` | {c['revalidation_scope']} |")
    return "\n".join(lines)
