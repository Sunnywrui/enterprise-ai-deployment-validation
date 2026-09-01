from __future__ import annotations
from .base import Adapter, ModelResponse

class ReplayAdapter(Adapter):
    def __init__(self, profile: dict):
        self.responses = profile.get("responses", {})
        self.default_latency_ms = profile.get("default_latency_ms", 500)
        self.cost_per_call_usd = profile.get("cost_per_call_usd", 0.01)

    def invoke(self, case: dict, repetition: int) -> ModelResponse:
        cid = case["case_id"]
        value = self.responses.get(cid, {})
        if isinstance(value, list):
            value = value[min(repetition - 1, len(value) - 1)]
        return ModelResponse(
            text=value.get("text", ""),
            tool_name=value.get("tool_name"),
            tool_arguments=value.get("tool_arguments"),
            raw=value,
            latency_ms=value.get("latency_ms", self.default_latency_ms),
            inference_cost_usd=value.get("inference_cost_usd", self.cost_per_call_usd),
        )
