# ADK Agent with MCP Tool (Step by Step)

This tutorial shows MCP from start to finish:

1. Define a simple MCP tool server
2. Run the MCP server as a separate process
3. Connect with a standalone MCP client
4. Connect with an ADK agent

## Concepts

- MCP server exposes tools (`create_note`, `list_notes`, `read_note`)
- A standalone MCP client can call those tools directly over HTTP (SSE)
- ADK connects to the same MCP server URL with `McpToolset`

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

## Step 1: Define the MCP tools

The MCP tool server is in:

- `tutorials/mcp_agent/notes_server.py`

It exposes three tools:

- `create_note(title, content)`
- `list_notes()`
- `read_note(title)`

## Step 2: Run MCP as standalone (without ADK)

Start the MCP server in its own terminal:

```bash
uv run python tutorials/mcp_agent/notes_server.py
```

This server listens on `http://127.0.0.1:9001/sse`.

## Step 3: Connect with the standalone MCP client

In another terminal (while server is running):

```bash
uv run python tutorials/mcp_agent/run_standalone_client.py
```

You should see:

- available tools
- a note being created
- a list of note files
- the note content being read back

## Step 4: Use the MCP tools from an ADK agent

Keep the MCP server terminal running, then in a new terminal run ADK:

```bash
export MCP_SERVER_URL="http://127.0.0.1:9001/sse"
uv run adk web tutorials/mcp_agent
```

Open [http://localhost:8000](http://localhost:8000), pick **filesystem**, and try:

- "Create a note titled shopping list with content eggs, milk, bread"
- "List my notes"
- "Read the shopping list note"

If your server runs on a different host/port, set `MCP_SERVER_URL` to that URL.

Cleaning up:
lsof -nP -iTCP:9001 -sTCP:LISTEN
kill <PID>