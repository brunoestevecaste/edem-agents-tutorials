"""Talk with Data agent: answers analytics questions using BigQuery tools."""

from google.adk import Agent

from tutorials.model_config import get_model

from src.project.services.bigquery_service import MockBigQueryService

bigquery = MockBigQueryService()


def list_tables() -> list[str]:
    """List available BigQuery tables."""
    return bigquery.list_tables()


def get_table_schema(table_name: str) -> dict:
    """Return the schema for a BigQuery table."""
    return bigquery.get_table_schema(table_name)


def run_read_only_query(sql: str) -> dict:
    """Run a read-only SQL query and return rows plus SQL."""
    result = bigquery.run_read_only_query(sql)
    return {"rows": result.rows, "sql": result.sql}


talk_with_data_agent = Agent(
    model=get_model(),
    name="talk_with_data_agent",
    description="Answers analytics questions by inspecting table schema and running read-only SQL.",
    instruction=(
        "You are a Talk with Data agent. Use ReAct: think about the next needed tool, call it, "
        "observe the result, then continue.\n"
        "Always call list_tables before choosing a table.\n"
        "Always call get_table_schema before writing SQL.\n"
        "Only run read-only SELECT queries with run_read_only_query.\n"
        "Do not run DELETE, UPDATE, INSERT, DROP, TRUNCATE, or ALTER.\n"
        "Answer with the result summary and the SQL used."
    ),
    tools=[list_tables, get_table_schema, run_read_only_query],
)
