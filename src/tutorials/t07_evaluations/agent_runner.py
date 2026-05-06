"""Run the multi-agent supervisor and capture its execution trace."""

import asyncio
from dataclasses import dataclass, field

from google.adk.runners import InMemoryRunner
from google.genai import types

import tutorials.t04_multi_agent.supervisor.agent as _supervisor_module

_APP_NAME = "evaluations"


@dataclass
class AgentTrace:
    final_response: str
    tools_called: list[str] = field(default_factory=list)
    steps: list[str] = field(default_factory=list)


async def _run_async(input_text: str) -> AgentTrace:
    runner = InMemoryRunner(agent=_supervisor_module.root_agent, app_name=_APP_NAME)
    session = await runner.session_service.create_session(
        app_name=_APP_NAME, user_id="eval_user"
    )

    trace = AgentTrace(final_response="")
    trace.steps.append(f"User: {input_text}")

    async for event in runner.run_async(
        user_id="eval_user",
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(text=input_text)]),
    ):
        for fc in event.get_function_calls():
            args = dict(fc.args or {})
            trace.tools_called.append(fc.name)
            trace.steps.append(f"Tool call → {fc.name}({args})")

        if event.get_function_responses():
            for fr in event.get_function_responses():
                trace.steps.append(f"Tool result ← {fr.name}: {fr.response}")

        if event.is_final_response() and event.content:
            for part in event.content.parts:
                if part.text:
                    trace.final_response = part.text
                    trace.steps.append(f"Final response: {part.text}")

    return trace


def run_agent(input_text: str) -> AgentTrace:
    """Run the supervisor agent synchronously and return its trace."""
    return asyncio.run(_run_async(input_text))
