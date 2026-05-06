"""DeepEval judge model adapter — mirrors model_config.py env var conventions.

Reads MODEL_PROVIDER and the provider-specific env vars exactly as model_config.py does.
Gemini and Groq are backed by LiteLLM; Vertex uses google.genai directly with ADC so
the judge runs against the same Vertex endpoint as the agent.
"""

import os

import litellm
from deepeval.models.base_model import DeepEvalBaseLLM


class _LiteLLMJudge(DeepEvalBaseLLM):
    def __init__(self, model: str) -> None:
        self.model = model

    def load_model(self) -> "_LiteLLMJudge":
        return self

    def generate(self, prompt: str) -> str:
        resp = litellm.completion(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content

    async def a_generate(self, prompt: str) -> str:
        resp = await litellm.acompletion(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content

    def get_model_name(self) -> str:
        return self.model


class _GenAIJudge(DeepEvalBaseLLM):
    """Judge that calls Vertex AI via google.genai using Application Default Credentials."""

    def __init__(self, model: str) -> None:
        self.model = model

    def load_model(self) -> "_GenAIJudge":
        return self

    def _get_client(self):
        from google import genai

        # Uses Application Default Credentials (gcloud auth application-default login).
        # Reads GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION from env.
        return genai.Client(vertexai=True)

    def generate(self, prompt: str) -> str:
        import asyncio

        return asyncio.run(self.a_generate(prompt))

    async def a_generate(self, prompt: str) -> str:
        response = await self._get_client().aio.models.generate_content(
            model=self.model,
            contents=prompt,
        )
        return response.text

    def get_model_name(self) -> str:
        return self.model


def get_judge_model() -> DeepEvalBaseLLM:
    """Return a DeepEval-compatible judge using the same provider as model_config.py."""
    provider = os.getenv("MODEL_PROVIDER", "gemini").lower()

    if provider == "groq":
        return _LiteLLMJudge(os.getenv("GROQ_MODEL", "groq/qwen/qwen3-32b"))

    if provider == "vertex":
        return _GenAIJudge(os.getenv("VERTEX_MODEL", "gemini-2.5-flash-lite"))

    # LiteLLM expects the "gemini/<model-name>" prefix for Gemini models
    return _LiteLLMJudge("gemini/" + os.getenv("GEMINI_MODEL", "gemma-3-27b-it"))
