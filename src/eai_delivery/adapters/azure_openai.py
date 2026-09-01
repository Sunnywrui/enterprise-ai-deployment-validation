from __future__ import annotations
import os
from .openai_compatible import OpenAICompatibleAdapter

class AzureOpenAIAdapter(OpenAICompatibleAdapter):
    def __init__(self, profile):
        mapped = dict(profile)
        endpoint = profile["azure_endpoint"].rstrip("/")
        deployment = profile["deployment_name"]
        api_version = profile.get("api_version","2024-10-21")
        mapped["base_url"] = f"{endpoint}/openai/deployments/{deployment}"
        mapped["path"] = f"/chat/completions?api-version={api_version}"
        mapped["model"] = deployment
        mapped["api_key"] = os.getenv(profile.get("api_key_env","AZURE_OPENAI_API_KEY"))
        mapped["headers"] = {**mapped.get("headers",{}), "api-key": mapped["api_key"] or ""}
        mapped["api_key_env"] = None
        super().__init__(mapped)
