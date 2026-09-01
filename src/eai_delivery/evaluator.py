from __future__ import annotations
import json
from dataclasses import dataclass
from .adapters.base import ModelResponse
from .tool_validation import validate_tool_arguments

@dataclass
class CaseResult:
    run_id: str
    case_id: str
    repetition: int
    mandatory: bool
    weight: float
    task_completed: int
    human_accepted: int | None
    semantic_score: float | None
    semantic_accepted: int | None
    tool_correct: int | None
    arguments_correct: int | None
    argument_schema_valid: int | None
    schema_valid: int | None
    permission_compliant: int
    latency_ms: float | None
    inference_cost_usd: float
    human_review_cost_usd: float
    retry_debug_cost_usd: float
    failure_loss_usd: float
    total_workflow_cost_usd: float
    failure_notes: str
    judge_source: str

def _subset(expected,actual):
    if isinstance(expected,dict):
        return isinstance(actual,dict) and all(k in actual and _subset(v,actual[k]) for k,v in expected.items())
    if isinstance(expected,list): return expected==actual
    return expected==actual

def evaluate_case(run_id,case,response,repetition,judge_result=None):
    failures=[]; text=response.text or ""; permission_ok=1
    req=case.get("expected_content_contains")
    if req and req.lower() not in text.lower(): failures.append(f"missing required content: {req}")
    forb=case.get("forbidden_content_contains")
    if forb and forb.lower() in text.lower():
        failures.append(f"forbidden content observed: {forb}"); permission_ok=0

    expected_tool=case.get("expected_tool"); tool_correct=None
    if expected_tool:
        tool_correct=int(response.tool_name==expected_tool)
        if not tool_correct: failures.append(f"tool expected={expected_tool}, actual={response.tool_name}")

    args_correct=None
    if case.get("expected_arguments") is not None:
        args_correct=int(_subset(case["expected_arguments"],response.tool_arguments or {}))
        if not args_correct: failures.append("tool arguments mismatch")

    arg_schema_valid=None
    if case.get("tool_arguments_schema_json"):
        ok,errs=validate_tool_arguments(case["tool_arguments_schema_json"],response.tool_arguments or {})
        arg_schema_valid=int(ok)
        if not ok: failures.append("tool argument schema invalid: "+" | ".join(e["message"] for e in errs))

    schema_valid=None
    if case.get("expect_json","").lower() in {"1","yes","true"}:
        try: json.loads(text); schema_valid=1
        except Exception: schema_valid=0; failures.append("response is not valid JSON")

    semantic_score=judge_result.score if judge_result else None
    semantic_accepted=judge_result.accepted if judge_result else None
    judge_source=judge_result.source if judge_result else ""
    if semantic_accepted==0: failures.append("semantic judge rejected result")

    auto=case.get("auto_human_accept","yes").lower() in {"1","yes","true"}
    task_completed=int(not failures)
    human_accepted=task_completed if auto else None
    if judge_result and judge_result.source=="human":
        human_accepted=judge_result.accepted
        if judge_result.accepted==0:
            failures.append("human review rejected result"); task_completed=0

    inference=float(response.inference_cost_usd or 0)
    review=float(case.get("human_review_cost_usd") or 0)
    retry=float(case.get("retry_debug_cost_usd") or 0) if not task_completed else 0
    loss=float(case.get("failure_loss_usd") or 0) if not task_completed else 0
    total=inference+review+retry+loss
    return CaseResult(run_id,case["case_id"],repetition,case["mandatory"],case["weight"],
        task_completed,human_accepted,semantic_score,semantic_accepted,tool_correct,args_correct,
        arg_schema_valid,schema_valid,permission_ok,response.latency_ms,inference,review,retry,loss,total,
        "; ".join(failures),judge_source)
