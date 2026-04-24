"""Orchestrator ADK app: exposes `root_agent` to the ADK Dev UI.

`adk web` discovers apps by scanning subfolders of the folder it was invoked on
for `agent.py` modules that define `root_agent`. Running `adk web src/project`
surfaces this package as the **orchestrator** app.
"""

import logging

for name in ("tools.bigquery_mcp_tools", "services.bigquery_service"):
    _lg = logging.getLogger(name)
    _lg.setLevel(logging.INFO)
    if not _lg.handlers:
        _handler = logging.StreamHandler()
        _handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s"))
        _lg.addHandler(_handler)
    _lg.propagate = True

from .agent import root_agent

__all__ = ["root_agent"]
