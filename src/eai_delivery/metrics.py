from __future__ import annotations
import math
from .stats import wilson_interval, mean_ci

BINARY_FIELDS={
"task_completion_rate":"task_completed","human_acceptance_rate":"human_accepted",
"semantic_acceptance_rate":"semantic_accepted","tool_call_accuracy":"tool_correct",
"argument_accuracy":"arguments_correct","argument_schema_validity":"argument_schema_valid",
"schema_validity":"schema_valid","permission_compliance":"permission_compliant"}

def _weighted_rate(results,field):
    vals=[(getattr(r,field),r.weight) for r in results if getattr(r,field) is not None]
    if not vals:return None
    denom=sum(w for _,w in vals); return sum(float(v)*w for v,w in vals)/denom if denom else None

def _percentile(values,q):
    xs=sorted(v for v in values if v is not None)
    if not xs:return None
    if len(xs)==1:return xs[0]
    pos=(len(xs)-1)*q; lo=math.floor(pos); hi=math.ceil(pos)
    if lo==hi:return xs[lo]
    return xs[lo]+(xs[hi]-xs[lo])*(pos-lo)

def aggregate(results):
    out={}; intervals={}
    for metric,field in BINARY_FIELDS.items():
        out[metric]=_weighted_rate(results,field)
        vals=[getattr(r,field) for r in results if getattr(r,field) is not None]
        if vals:
            lo,hi=wilson_interval(sum(int(v) for v in vals),len(vals))
            intervals[metric]={"lower":lo,"upper":hi,"n":len(vals),"method":"Wilson 95%"}
    sem=[r.semantic_score for r in results if r.semantic_score is not None]
    if sem:
        mean,lo,hi=mean_ci(sem); out["semantic_score_mean"]=mean
        intervals["semantic_score_mean"]={"lower":lo,"upper":hi,"n":len(sem),"method":"Normal approx 95%"}
    out["p95_latency_ms"]=_percentile([r.latency_ms for r in results],0.95)
    accepted=sum(1 for r in results if r.human_accepted==1); total=sum(r.total_workflow_cost_usd for r in results)
    out["total_effective_cost_usd"]=total
    out["cost_per_accepted_workflow"]=(total/accepted) if accepted else None
    out["case_runs"]=len(results); out["accepted_runs"]=accepted; out["confidence_intervals"]=intervals
    return out
