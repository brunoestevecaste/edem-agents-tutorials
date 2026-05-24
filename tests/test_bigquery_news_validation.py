"""Tests for local SQL safety validation."""

import pytest

from ai_news_journalist.retrieval.bigquery_news import validate_read_only_sql


def test_validate_read_only_sql_allows_semicolon_inside_string_literal():
    sql = "SELECT REGEXP_REPLACE(name, r',\\d+;', ';') AS clean_name"

    validate_read_only_sql(sql)


def test_validate_read_only_sql_rejects_multiple_statements():
    sql = "SELECT name FROM dataset.table; DROP TABLE dataset.table"

    with pytest.raises(ValueError, match="Only one SQL statement"):
        validate_read_only_sql(sql)
