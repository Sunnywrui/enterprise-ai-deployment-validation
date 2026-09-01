from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass
class ModelResponse:
    text: str = ""
    tool_name: str | None = None
    tool_arguments: dict[str, Any] | None = None
    raw: dict[str, Any] = field(default_factory=dict)
    latency_ms: float | None = None
    inference_cost_usd: float | None = None

class Adapter:
    def invoke(self, case: dict, repetition: int) -> ModelResponse:
        raise NotImplementedError
