
from .replay import ReplayAdapter
from .openai_compatible import OpenAICompatibleAdapter

def create_adapter(profile):
    kind = profile.get("adapter")
    if kind == "replay":
        return ReplayAdapter(profile)
    if kind == "openai_compatible":
        return OpenAICompatibleAdapter(profile)
    if kind == "azure_openai":
        from .azure_openai import AzureOpenAIAdapter
        return AzureOpenAIAdapter(profile)
    if kind == "bedrock":
        from .bedrock import BedrockAdapter
        return BedrockAdapter(profile)
    if kind == "vertex":
        from .vertex import VertexAdapter
        return VertexAdapter(profile)
    raise ValueError(f"Unknown adapter: {kind}")
