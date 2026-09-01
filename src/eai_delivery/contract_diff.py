from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any

MATERIAL_PATHS = {
    "model": [
        "model_identity.model_id", "model_identity.revision", "model_identity.checkpoint",
        "model_identity.fine_tune_or_adapter"
    ],
    "artifact": [
        "deployment_artifact.artifact_hash", "deployment_artifact.quantization",
        "deployment_artifact.precision", "deployment_artifact.tokenizer"
    ],
    "runtime": [
        "serving_runtime.engine", "serving_runtime.version", "serving_runtime.container_digest",
        "serving_runtime.kernels_or_backend", "serving_runtime.tensor_parallel_size",
        "serving_runtime.pipeline_parallel_size"
    ],
    "hardware": [
        "serving_runtime.accelerator", "serving_runtime.cuda_version", "serving_runtime.driver_version"
    ],
    "protocol": [
        "agent_protocol.system_prompt", "agent_protocol.chat_template",
        "agent_protocol.tool_calling", "agent_protocol.structured_output", "agent_protocol.connectors"
    ],
    "inference": ["inference_configuration"],
    "enterprise": ["enterprise_environment"],
    "business": ["business_contract"]
}

REVALIDATION = {
    "model": "Full or risk-targeted Golden Eval",
    "artifact": "Full critical-path + economics",
    "runtime": "Targeted behavior + performance",
    "hardware": "Performance + critical accuracy/tool tests",
    "protocol": "Full affected Agent/structured-output regression",
    "inference": "Targeted behavior + latency/cost",
    "enterprise": "Affected workflow + governance",
    "business": "Re-acceptance and threshold review",
}

def get_path(obj: dict, path: str):
    cur: Any = obj
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur

def diff_contracts(old: dict, new: dict):
    changes = []
    for domain, paths in MATERIAL_PATHS.items():
        for path in paths:
            a, b = get_path(old, path), get_path(new, path)
            if a != b:
                changes.append({
                    "domain": domain,
                    "field": path,
                    "reference": a,
                    "target": b,
                    "material": True,
                    "revalidation_scope": REVALIDATION[domain]
                })
    return changes
