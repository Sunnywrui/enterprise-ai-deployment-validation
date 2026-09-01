from __future__ import annotations
import json, os, time
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from .base import Adapter, ModelResponse

class OpenAICompatibleAdapter(Adapter):
    def __init__(self, profile):
        self.base_url = profile["base_url"].rstrip("/")
        self.model = profile["model"]
        self.timeout = int(profile.get("timeout_seconds",90))
        env = profile.get("api_key_env")
        self.api_key = os.getenv(env) if env else profile.get("api_key")
        self.extra_headers = profile.get("headers",{})
        self.default_params = profile.get("parameters",{})
        self.path = profile.get("path","/chat/completions")

    def invoke(self, case, repetition):
        messages=[]
        if case.get("system_prompt"):
            messages.append({"role":"system","content":case["system_prompt"]})
        messages.append({"role":"user","content":case.get("input_or_trigger","")})
        body={"model":self.model,"messages":messages,**self.default_params}
        if case.get("tools_json"):
            body["tools"]=json.loads(case["tools_json"]); body["tool_choice"]="auto"
        headers={"Content-Type":"application/json",**self.extra_headers}
        if self.api_key: headers["Authorization"]=f"Bearer {self.api_key}"
        req=Request(f"{self.base_url}{self.path}",data=json.dumps(body).encode(),headers=headers,method="POST")
        started=time.perf_counter()
        try:
            with urlopen(req,timeout=self.timeout) as resp:
                payload=json.loads(resp.read().decode())
        except HTTPError as e:
            raise RuntimeError(f"HTTP {e.code}: {e.read().decode(errors='replace')}") from e
        latency=(time.perf_counter()-started)*1000
        msg=payload["choices"][0]["message"]; text=msg.get("content") or ""
        tool_name=None; tool_args=None
        calls=msg.get("tool_calls") or []
        if calls:
            fn=calls[0].get("function",{}); tool_name=fn.get("name"); args=fn.get("arguments")
            if isinstance(args,str):
                try: tool_args=json.loads(args)
                except Exception: tool_args={"__raw__":args}
            elif isinstance(args,dict): tool_args=args
        return ModelResponse(text=text,tool_name=tool_name,tool_arguments=tool_args,raw=payload,latency_ms=latency)
