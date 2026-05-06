.PHONY: lint lint-fix format format-check fix check test

lint:
	uv run ruff check src/

lint-fix:
	uv run ruff check --fix src/

format:
	uv run ruff format src/

format-check:
	uv run ruff format --check src/

fix: lint-fix format

check: lint format-check

test:
	uv run pytest
