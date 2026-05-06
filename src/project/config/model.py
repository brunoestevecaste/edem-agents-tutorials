"""Model configuration — switch between Gemini, Groq, and Vertex via MODEL_PROVIDER.

Self-contained so the project does not depend on the tutorials package.

Providers:
  gemini (default) — AI Studio API, requires GOOGLE_API_KEY
  groq             — requires GROQ_API_KEY
  vertex           — Vertex AI with Application Default Credentials (ADC).
                     Requires:
                       1. `gcloud auth application-default login` (one-time)
                       2. GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION env vars
"""

from __future__ import annotations

import os


def get_model():
    provider = os.getenv("MODEL_PROVIDER", "gemini").lower()

    if provider == "groq":
        from google.adk.models.lite_llm import LiteLlm

        return LiteLlm(model=os.getenv("GROQ_MODEL", "groq/qwen/qwen3-32b"))

    if provider == "gemini":
        from google.adk.models.lite_llm import LiteLlm

        return LiteLlm(model=os.getenv("GEMINI_MODEL", "gemma-3-27b-it"))

    if provider == "vertex":
        os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")
        return os.getenv("VERTEX_MODEL", "gemini-2.5-flash-lite")

    return os.getenv("GEMINI_MODEL", "gemma-3-27b-it")
