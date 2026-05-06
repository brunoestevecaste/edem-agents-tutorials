# Remote A2A Agents (ADK + Gemini/Groq + A2A)

Three remote agents communicating via A2A: a dice roller, a stats calculator, and a supervisor that orchestrates both.

## Setup

```bash
uv sync --extra adk
```

### Option A: Gemini (default)

Generate an API key at https://aistudio.google.com/:

```bash
export GOOGLE_API_KEY="your-gemini-api-key"
```

### Option B: Groq

Get an API key at https://console.groq.com/:

```bash
export MODEL_PROVIDER=groq
export GROQ_API_KEY="your-groq-api-key"
```

Uses `groq/qwen/qwen3-32b` by default. Override with `export GROQ_MODEL="groq/llama-3.3-70b-versatile"`.

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

Start all three agents, then the UI:

```bash
export PYTHONPATH=src
uv run uvicorn tutorials.t06_remote_a2a.roll_die.agent:a2a_app --host localhost --port 8001 & \
uv run uvicorn tutorials.t06_remote_a2a.stats.agent:a2a_app --host localhost --port 8002 & \
uv run uvicorn tutorials.t06_remote_a2a.supervisor.agent:a2a_app --host localhost --port 8003 &
```

```bash
uv run adk web src/tutorials/t06_remote_a2a
```

Open http://localhost:8000, pick **supervisor**, then try: **"Roll a 6-sided die 5 times and give me the stats"**.

To stop all agents: `kill %1 %2 %3` or `pkill -f uvicorn`.
