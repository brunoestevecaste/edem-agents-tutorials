# Tutorial Agent

A minimal ADK starter agent with one mock tool that returns the current time for a city.

## Concepts

- `Agent` with a model, name, description, and instruction
- Python function as an agent tool
- Smallest runnable tutorial structure

## Setup

```bash
uv sync --extra adk
```

## Run

```bash
uv run adk web src/tutorials/t01_tutorial_agent
```

Open http://localhost:8000, pick **root_agent**, and try:

- "What time is it in Madrid?"
- "Tell me the current time in Tokyo"
