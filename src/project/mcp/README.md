# MCP Layer Notes

This folder provides a teaching-oriented MCP layout for BigQuery-backed tools.

## Files
- `tools.yaml`: conceptual template showing a BigQuery source plus three tools.
- `bigquery_mcp_server.py`: minimal custom MCP server example exposing equivalent operations.

## Version Compatibility Note
Different MCP toolbox builds may require slightly different YAML fields (for auth, dataset scoping, or tool declarations). If your local toolbox rejects this file, keep `tools.yaml` as a conceptual template and adapt syntax to your installed version.

## Security Guidance
The demo server and tool wrappers are **read-only by policy**. Destructive SQL keywords are blocked in service logic.
