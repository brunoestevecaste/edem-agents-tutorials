# Sequential Workflow Agent

A deterministic pipeline where two agents run in a **fixed order** defined in code, not decided by an LLM. The researcher agent always runs first, the summarizer agent always runs second.

## Concepts

- `SequentialAgent`: runs sub-agents in list order (no LLM in the orchestrator)
- Deterministic workflow: the execution order is hardcoded, not agentic
- Each sub-agent is a full `LlmAgent` with its own tools

## How it differs from Multi-Agent

| | Multi-Agent (tutorial 2) | Sequential Workflow (this tutorial) |
| --- | --- | --- |
| **Orchestrator** | LlmAgent (supervisor) | SequentialAgent (code) |
| **Order** | LLM decides | Fixed in code |
| **LLM calls** | Supervisor + sub-agents | Only sub-agents |
| **Pattern** | Agentic / ReAct | Deterministic pipeline |

## Setup

```bash
uv sync --extra adk
```

### Option A: Gemini (default)

```bash
export GOOGLE_API_KEY="your-gemini-api-key"
```

### Option B: Groq

```bash
export MODEL_PROVIDER=groq
export GROQ_API_KEY="your-groq-api-key"
```

### Option C: Vertex AI

One-time auth on your machine:

```bash
gcloud auth application-default login
```

Then configure the provider:

```bash
export MODEL_PROVIDER=vertex
export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
export GOOGLE_CLOUD_LOCATION="global"
# optional
export VERTEX_MODEL="gemini-2.5-flash-lite"
```

## Run

```bash
uv run adk web src/tutorials/t03_sequential_agent
```

Open [http://localhost:8000](http://localhost:8000), pick **pipeline**, and try:

- "Tell me about Python"
- "What is Kubernetes?"
- "Explain MCP"
- "What are AI agents?"

The researcher looks up facts first, then the summarizer formats a structured report.
