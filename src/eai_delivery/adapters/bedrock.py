from __future__ import annotations
import time
from .base import Adapter, ModelResponse

class BedrockAdapter(Adapter):
    def __init__(self, profile):
        import boto3
        self.client=boto3.client("bedrock-runtime",region_name=profile.get("region"))
        self.model_id=profile["model_id"]
        self.inference_config=profile.get("inference_config",{})

    def invoke(self, case, repetition):
        kwargs={"modelId":self.model_id,
                "messages":[{"role":"user","content":[{"text":case.get("input_or_trigger","")}]}],
                "inferenceConfig":self.inference_config}
        started=time.perf_counter(); payload=self.client.converse(**kwargs)
        latency=(time.perf_counter()-started)*1000
        blocks=payload.get("output",{}).get("message",{}).get("content",[])
        text="".join(b.get("text","") for b in blocks if "text" in b)
        tool_name=None; tool_args=None
        for b in blocks:
            if "toolUse" in b:
                tool_name=b["toolUse"].get("name"); tool_args=b["toolUse"].get("input"); break
        return ModelResponse(text=text,tool_name=tool_name,tool_arguments=tool_args,raw=payload,latency_ms=latency)
