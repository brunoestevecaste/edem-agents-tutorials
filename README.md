# agents-tutorials

Agents tutorials and examples.

## Setup

Requires [uv](https://docs.astral.sh/uv/).

```bash
# Create venv and install project + dev dependencies
uv sync

# Run tests
uv run pytest

# Run a script
uv run python -c "from agents_tutorials import __version__; print(__version__)"
```

## Project structure

```
├── notebooks/          # Jupyter notebooks
├── src/
│   └── agents_tutorials/
├── tutorials/          # Step-by-step tutorials (ADK, A2A, etc.)
├── tests/
├── pyproject.toml
└── README.md
```

## Tutorials

All tutorials use the same dependency group:

```bash
uv sync --extra adk
```

### 1. Basic ADK Agent

A single agent with one Python function tool (dice rolling). See `tutorials/basic_agent/README.md`.

### 2. Multi-Agent (Local)

A supervisor agent orchestrating two local sub-agents (dice roller + stats calculator) using `AgentTool`. See `tutorials/multi_agent/README.md`.

### 3. ADK Agent with MCP Tool

A step-by-step MCP tutorial: run a separate notes MCP server and connect to it from both a standalone client and an ADK agent. See `tutorials/mcp_agent/README.md`.

### 4. Remote A2A Agents

Three remote agents communicating via the A2A protocol, each with its own agent card and HTTP server. See `tutorials/remote_a2a/README.md`.

## Notebooks

Install notebook dependencies and start Jupyter:

```bash
uv sync --extra notebooks
uv run jupyter notebook notebooks/
```
