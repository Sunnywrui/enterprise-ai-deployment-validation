from pathlib import Path
import uuid,yaml
from .adapters import create_adapter
from .golden import load_golden_csv
from .evaluator import evaluate_case
from .metrics import aggregate
from .compare import compare_metrics
from .reporting import write_case_results,write_json,write_delta_csv,write_release_md
from .judges import DeterministicSemanticJudge,LLMJudge,load_human_reviews

def _judge(case,response,judge_profile,human_reviews,repetition):
    key=(case["case_id"],repetition)
    if key in human_reviews:return human_reviews[key]
    mode=(case.get("judge_mode") or "deterministic").lower()
    if mode=="none":return None
    if mode=="llm":
        if not judge_profile: raise ValueError("judge_mode=llm but no judge profile configured")
        return LLMJudge(judge_profile).judge(case,response)
    return DeterministicSemanticJudge().judge(case,response)

def run_profile(profile,golden_path,judge_profile=None,human_review_path=None):
    adapter=create_adapter(profile); cases=load_golden_csv(golden_path); run_id=profile.get("run_id") or str(uuid.uuid4())
    default_reps=int(profile.get("repetitions_per_case",1)); human=load_human_reviews(human_review_path); results=[]
    for case in cases:
        reps=int(case.get("repetitions") or default_reps)
        for n in range(1,reps+1):
            resp=adapter.invoke(case,n)
            results.append(evaluate_case(run_id,case,resp,n,_judge(case,resp,judge_profile,human,n)))
    return results,aggregate(results)

def compare_profiles(reference_profile,target_profile,golden_path,thresholds_path,out_dir,judge_profile=None,human_review_path=None):
    out=Path(out_dir); out.mkdir(parents=True,exist_ok=True)
    rr,rm=run_profile(reference_profile,golden_path,judge_profile,human_review_path)
    tr,tm=run_profile(target_profile,golden_path,judge_profile,human_review_path)
    thresholds=yaml.safe_load(Path(thresholds_path).read_text())
    rows,decision=compare_metrics(rm,tm,thresholds)
    write_case_results(out/"reference_case_results.csv",rr); write_case_results(out/"target_case_results.csv",tr)
    write_json(out/"reference_metrics.json",rm); write_json(out/"target_metrics.json",tm)
    write_json(out/"deployment_delta.json",{"metrics":rows,"decision":decision}); write_delta_csv(out/"deployment_delta.csv",rows)
    write_release_md(out/"release_decision.md",decision,rows,reference_profile.get("deployment_id","reference"),target_profile.get("deployment_id","target"))
    return decision
