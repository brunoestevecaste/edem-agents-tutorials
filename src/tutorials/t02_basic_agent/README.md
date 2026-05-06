# Basic ADK Agent

The simplest ADK agent: a single agent with one Python function tool that rolls dice.

## Concepts

- `Agent` with `instruction`, `description`, and `tools`
- Python function as an agent tool
- Running agents with `adk web`

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
uv run adk web src/tutorials/t02_basic_agent
```

Open http://localhost:8000, pick **roll_die**, and try:

- "Roll a 6-sided die 3 times"
- "Roll a 20-sided die"
- "Roll a die 10 times"
