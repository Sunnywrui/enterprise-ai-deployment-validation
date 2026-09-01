from __future__ import annotations
import csv, json
from dataclasses import dataclass
from pathlib import Path
from .adapters import create_adapter

@dataclass
class JudgeResult:
    score: float | None
    accepted: int | None
    rationale: str = ""
    source: str = ""

class DeterministicSemanticJudge:
    def judge(self, case, response):
        concepts = [x.strip().lower() for x in (case.get("semantic_required_concepts") or "").split("|") if x.strip()]
        if not concepts:
            return JudgeResult(None, None, "", "deterministic")
        text = (response.text or "").lower()
        hits = sum(1 for c in concepts if c in text)
        score = hits / len(concepts)
        threshold = float(case.get("semantic_threshold") or 0.8)
        return JudgeResult(score, int(score >= threshold), f"{hits}/{len(concepts)} required concepts matched", "deterministic")

class LLMJudge:
    def __init__(self, profile):
        self.adapter = create_adapter(profile)

    def judge(self, case, response):
        rubric = case.get("semantic_rubric") or case.get("human_acceptance_criteria") or "Judge business correctness."
        prompt = (
            "You are an enterprise AI evaluator. Return STRICT JSON with keys: "
            "score (0..1), accepted (true/false), rationale.\n"
            f"Rubric: {rubric}\n"
            f"Input: {case.get('input_or_trigger','')}\n"
            f"Candidate response: {response.text}"
        )
        judged = self.adapter.invoke({"case_id":"judge","input_or_trigger":prompt}, 1)
        try:
            obj = json.loads(judged.text)
            return JudgeResult(float(obj["score"]), int(bool(obj["accepted"])), str(obj.get("rationale","")), "llm")
        except Exception as e:
            return JudgeResult(None, None, f"judge parse failure: {e}; raw={judged.text[:300]}", "llm")

def load_human_reviews(path):
    if not path: return {}
    out = {}
    with Path(path).open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            key = (row["case_id"], int(row.get("repetition") or 1))
            out[key] = JudgeResult(
                float(row["score"]) if row.get("score") else None,
                int(str(row.get("accepted","")).lower() in {"1","true","yes","y"}),
                row.get("rationale",""), "human"
            )
    return out
