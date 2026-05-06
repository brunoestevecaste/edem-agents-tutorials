# Multi-Agent (Local, no A2A)

A supervisor agent that orchestrates two local sub-agents -- a dice roller and a stats calculator -- using `AgentTool`. No network, no A2A protocol, no uvicorn.

## Concepts

- `AgentTool`: wraps an agent so it can be called as a tool (call-and-return)
- Multi-agent orchestration within a single process
- Supervisor pattern: one agent coordinates others

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
uv run adk web src/tutorials/t04_multi_agent
```

Open http://localhost:8000, pick **supervisor**, and try:

- "Roll a 6-sided die 5 times and give me the stats"
- "Roll a 20-sided die 10 times, then compute the mean and standard deviation"
