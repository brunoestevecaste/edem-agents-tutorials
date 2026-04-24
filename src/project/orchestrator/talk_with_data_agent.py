"""Talk with Data agent: answers analytics questions using BigQuery tools."""

from google.adk import Agent

from config.model import get_model
from tools.bigquery_mcp_tools import BigQueryMcpTools

bigquery_tools = BigQueryMcpTools.from_settings()


def list_tables() -> list[str]:
    """List available BigQuery tables."""
    return bigquery_tools.list_tables()


def get_table_schema(table_name: str) -> dict:
    """Return the schema for a BigQuery table."""
    return bigquery_tools.get_table_schema(table_name)


def run_read_only_query(sql: str) -> dict:
    """Run a read-only SQL query and return rows plus SQL."""
    return bigquery_tools.run_read_only_query_json(sql)


talk_with_data_agent = Agent(
    model=get_model(),
    name="talk_with_data_agent",
    description="Answers TheLook ecommerce analytics questions with read-only BigQuery SQL.",
    instruction=(
        "You are the Talk with Data agent for TheLook Retail Intelligence Assistant.\n"
        "Use BigQuery public dataset bigquery-public-data.thelook_ecommerce.\n"
        "Focus on these tables: users, orders, order_items, products, inventory_items.\n"
        "Useful joins: orders.user_id = users.id; order_items.order_id = orders.order_id; "
        "order_items.product_id = products.id; inventory_items.product_id = products.id.\n"
        "Use ReAct: think about the next needed tool, call it, observe the result, then continue.\n"
        "Always call list_tables before choosing a table.\n"
        "Always call get_table_schema before writing SQL.\n"
        "Only run read-only SELECT queries with selected columns, filters when useful, and LIMIT for detail rows.\n"
        "Do not run DELETE, UPDATE, INSERT, DROP, TRUNCATE, or ALTER.\n"
        "Answer with the result summary and the SQL used."
    ),
    tools=[list_tables, get_table_schema, run_read_only_query],
)
