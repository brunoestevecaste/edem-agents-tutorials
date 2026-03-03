"""Model configuration — switch between Gemini and Groq via MODEL_PROVIDER env var.

Usage in agent files:
    from tutorials.model_config import get_model
    root_agent = Agent(model=get_model(), ...)

Set MODEL_PROVIDER=groq to use Groq (requires GROQ_API_KEY).
Default is Gemini (requires GOOGLE_API_KEY).
"""

import os


def get_model():
    provider = os.getenv("MODEL_PROVIDER", "gemini").lower()

    if provider == "groq":
        from google.adk.models.lite_llm import LiteLlm

        return LiteLlm(model=os.getenv("GROQ_MODEL", "groq/qwen/qwen3-32b"))

    return os.getenv("GEMINI_MODEL", "gemma-3-27b-it")
