"""Model configuration — switch between Gemini, Groq, and Vertex via MODEL_PROVIDER env var.

Usage in agent files:
    from tutorials.model_config import get_model
    root_agent = Agent(model=get_model(), ...)

Providers:
  gemini (default) — AI Studio API, requires GOOGLE_API_KEY
  groq             — requires GROQ_API_KEY
  vertex           — Vertex AI with Application Default Credentials (ADC).
                     Requires:
                       1. `gcloud auth application-default login` (one-time)
                       2. GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION env vars
"""

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
        # The ADK's built-in Gemini class is used when the model is a plain string.
        # It builds genai.Client() which reads these env vars and uses ADC:
        #   GOOGLE_GENAI_USE_VERTEXAI → route to aiplatform.googleapis.com
        #   GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION → target project/region
        # ADC comes from `gcloud auth application-default login` or a service account.
        os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")
        return os.getenv("VERTEX_MODEL", "gemini-2.5-flash-lite")

    return os.getenv("GEMINI_MODEL", "gemma-3-27b-it")


def get_embedding_model():
    """Return the embedding model configured for the current provider."""
    from llama_index.embeddings.google_genai import GoogleGenAIEmbedding

    provider = os.getenv("MODEL_PROVIDER", "gemini").lower()
    model_name = os.getenv("LOCAL_RAG_EMBEDDING_MODEL", "text-embedding-004")

    if provider == "vertex":
        project = os.getenv("GOOGLE_CLOUD_PROJECT", "").strip()
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "").strip()
        if not project or not location:
            raise RuntimeError(
                "Vertex embeddings require GOOGLE_CLOUD_PROJECT and "
                "GOOGLE_CLOUD_LOCATION env vars."
            )

        os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")
        return GoogleGenAIEmbedding(
            model_name=model_name,
            vertexai_config={"project": project, "location": location},
        )

    google_api_key = os.getenv("GOOGLE_API_KEY", "").strip()
    if not google_api_key:
        raise RuntimeError(
            "Gemini API embeddings require GOOGLE_API_KEY. To use Vertex AI "
            "embeddings, set MODEL_PROVIDER=vertex plus GOOGLE_CLOUD_PROJECT "
            "and GOOGLE_CLOUD_LOCATION."
        )

    return GoogleGenAIEmbedding(
        model_name=model_name,
        api_key=google_api_key,
    )
