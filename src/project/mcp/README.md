# MCP Layer Notes

This folder provides a teaching-oriented MCP layout for TheLook ecommerce BigQuery tools.

## Files
- `tools.yaml`: conceptual template showing a BigQuery source plus three tools.
- `bigquery_mcp_server.py`: minimal custom MCP server exposing the same service-backed operations used by the ADK agent.

## Version Compatibility Note
Different MCP toolbox builds may require slightly different YAML fields (for auth, dataset scoping, or tool declarations). If your local toolbox rejects this file, keep `tools.yaml` as a conceptual template and adapt syntax to your installed version.

## Security Guidance
The server and tool wrappers are **read-only by policy**. SQL is validated before execution, real BigQuery queries run a dry run first, queries are scoped to `bigquery-public-data.thelook_ecommerce`, and `BIGQUERY_MAX_BYTES_BILLED` limits scan cost.

Set `USE_MOCK_SERVICES=true` for local mock data, or `USE_MOCK_SERVICES=false` with `GOOGLE_CLOUD_PROJECT`, `BIGQUERY_DATASET_PROJECT`, `BIGQUERY_DATASET`, and ADC configured for real BigQuery.
