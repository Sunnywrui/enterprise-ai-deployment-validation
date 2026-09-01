from __future__ import annotations
import json, time
from urllib.request import Request, urlopen
from google.auth import default
from google.auth.transport.requests import Request as GoogleAuthRequest
from .base import Adapter, ModelResponse

class VertexAdapter(Adapter):
    def __init__(self, profile):
        self.project=profile["project"]; self.location=profile.get("location","us-central1")
        self.model=profile["model"]; self.publisher=profile.get("publisher","google")
        self.timeout=int(profile.get("timeout_seconds",90)); self.params=profile.get("parameters",{})
        self.credentials,_=default(scopes=["https://www.googleapis.com/auth/cloud-platform"])

    def invoke(self, case, repetition):
        self.credentials.refresh(GoogleAuthRequest())
        url=(f"https://{self.location}-aiplatform.googleapis.com/v1/projects/{self.project}/"
             f"locations/{self.location}/publishers/{self.publisher}/models/{self.model}:generateContent")
        body={"contents":[{"role":"user","parts":[{"text":case.get("input_or_trigger","")}]}],
              "generationConfig":self.params}
        req=Request(url,data=json.dumps(body).encode(),headers={
            "Authorization":f"Bearer {self.credentials.token}",
            "Content-Type":"application/json"},method="POST")
        started=time.perf_counter()
        with urlopen(req,timeout=self.timeout) as resp:
            payload=json.loads(resp.read().decode())
        latency=(time.perf_counter()-started)*1000
        parts=payload.get("candidates",[{}])[0].get("content",{}).get("parts",[])
        text="".join(p.get("text","") for p in parts if "text" in p)
        tool_name=None; tool_args=None
        for p in parts:
            if p.get("functionCall"):
                tool_name=p["functionCall"].get("name"); tool_args=p["functionCall"].get("args"); break
        return ModelResponse(text=text,tool_name=tool_name,tool_arguments=tool_args,raw=payload,latency_ms=latency)
