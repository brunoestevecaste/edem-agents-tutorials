"""Minimal MCP server for a beginner-friendly notes tool tutorial."""

from __future__ import annotations

from pathlib import Path

from mcp.server import FastMCP

mcp = FastMCP(
    name="notes-mcp-server",
    host="127.0.0.1",
    port=9001,
)

NOTES_DIR = Path(__file__).parent / "filesystem" / "sandbox" / "notes"


def _notes_dir() -> Path:
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    return NOTES_DIR


def _note_path(title: str) -> Path:
    clean_title = title.strip()
    if not clean_title:
        raise ValueError("title cannot be empty")

    safe_title = "".join(ch for ch in clean_title if ch.isalnum() or ch in ("-", "_", " ", "."))
    safe_title = safe_title.strip().replace(" ", "_")
    if not safe_title:
        raise ValueError("title must contain letters or numbers")

    if not safe_title.lower().endswith(".txt"):
        safe_title = f"{safe_title}.txt"

    return _notes_dir() / safe_title


@mcp.tool(description="Create or overwrite a note by title.")
def create_note(title: str, content: str) -> str:
    note_path = _note_path(title)
    note_path.write_text(content, encoding="utf-8")
    return f"Saved note: {note_path.name}"


@mcp.tool(description="List all notes.")
def list_notes() -> list[str]:
    notes_dir = _notes_dir()
    return sorted(path.name for path in notes_dir.glob("*.txt"))


@mcp.tool(description="Read a note by title.")
def read_note(title: str) -> str:
    note_path = _note_path(title)
    if not note_path.exists():
        return f"Note not found: {note_path.name}"
    return note_path.read_text(encoding="utf-8")


if __name__ == "__main__":
    # Run as an independent SSE server so clients can connect over HTTP.
    mcp.run(transport="sse")
