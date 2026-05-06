"""DeepEval evaluation suite for the multi-agent supervisor.

Each test function covers one metric. Run the full suite with:

    uv run pytest -v

All metrics use the same judge model as the agent itself (controlled by
MODEL_PROVIDER / GEMINI_MODEL / GROQ_MODEL env vars).
"""

from deepeval import assert_test
from deepeval.dataset import Golden
from deepeval.metrics import (
    GEval,
    PlanQualityMetric,
    StepEfficiencyMetric,
    TaskCompletionMetric,
    ToolCorrectnessMetric,
)
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

from tutorials.t07_evaluations.agent_runner import AgentTrace, run_agent
from tutorials.t07_evaluations.dataset import dataset
from tutorials.t07_evaluations.judge_model import get_judge_model


# ── helpers ───────────────────────────────────────────────────────────────────


def _build_test_case(golden: Golden) -> tuple[LLMTestCase, AgentTrace]:
    """Run the agent for a Golden and return a populated LLMTestCase."""
    trace = run_agent(golden.input)
    test_case = LLMTestCase(
        input=golden.input,
        actual_output=trace.final_response,
        expected_output=golden.expected_output,
        tools_called=trace.tools_called,
        expected_tools=golden.expected_tools,
    )
    return test_case, trace


def _trace_as_text(trace: AgentTrace) -> str:
    """Format trace steps as a numbered string for trace-based metrics."""
    return "\n".join(f"{i + 1}. {step}" for i, step in enumerate(trace.steps))


# ── metric tests ──────────────────────────────────────────────────────────────


def test_task_completion():
    """Did the agent actually solve the user's request end-to-end?

    TaskCompletionMetric uses an LLM-as-judge to assess whether the final
    response accomplishes what the user asked for.
    """
    test_case, _ = _build_test_case(dataset.goldens[0])  # Roll 5d6 + stats

    metric = TaskCompletionMetric(threshold=0.7, model=get_judge_model())
    assert_test(test_case, [metric])


def test_tool_correctness():
    """Did the agent invoke the right sub-agents in the right order?

    ToolCorrectnessMetric compares the actual tool call sequence against
    expected_tools from the Golden. No LLM judge needed — deterministic.
    """
    test_case, _ = _build_test_case(dataset.goldens[0])

    metric = ToolCorrectnessMetric(threshold=0.8)
    assert_test(test_case, [metric])


def test_step_efficiency():
    """Did the agent complete the task without unnecessary extra steps?

    StepEfficiencyMetric evaluates whether the execution trace shows redundant
    or wasteful tool calls (e.g. re-rolling the same die, calling stats twice).
    The full trace is passed as actual_output so the judge can inspect each step.
    """
    test_case, trace = _build_test_case(dataset.goldens[0])

    trace_case = LLMTestCase(
        input=test_case.input,
        actual_output=_trace_as_text(trace),
        expected_output=test_case.expected_output,
        tools_called=test_case.tools_called,
        expected_tools=test_case.expected_tools,
    )
    metric = StepEfficiencyMetric(threshold=0.7, model=get_judge_model())
    assert_test(trace_case, [metric])


def test_plan_quality():
    """Was the supervisor's orchestration plan sensible before it started executing?

    PlanQualityMetric extracts the implicit plan from the trace and evaluates
    whether it was a reasonable approach to accomplish the task.
    Uses a different golden (3d20) to show the metric generalises.
    """
    test_case, trace = _build_test_case(dataset.goldens[1])  # Roll 3d20 + stats

    trace_case = LLMTestCase(
        input=test_case.input,
        actual_output=_trace_as_text(trace),
        expected_output=test_case.expected_output,
        tools_called=test_case.tools_called,
        expected_tools=test_case.expected_tools,
    )
    metric = PlanQualityMetric(threshold=0.7, model=get_judge_model())
    assert_test(trace_case, [metric])


def test_custom_metric_numerical_presence():
    """Custom GEval: does the output contain actual roll values, mean, and std?

    This is a domain-specific metric that checks three concrete requirements:
      1. Individual dice roll results appear as explicit numbers.
      2. A computed mean value is present.
      3. A computed standard deviation value is present.

    GEval lets you define such criteria in natural language and uses the judge
    model to score the output against them.
    """
    test_case, _ = _build_test_case(dataset.goldens[0])

    metric = GEval(
        name="Numerical Presence",
        criteria=(
            "Evaluate whether the output contains ALL THREE of the following: "
            "(1) the individual dice roll results as explicit numbers, "
            "(2) a clearly labeled computed mean value, "
            "(3) a clearly labeled computed standard deviation value. "
            "Score 1.0 if all three are present. "
            "Deduct proportionally for each missing component (0.33 per missing item)."
        ),
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
        threshold=0.75,
        model=get_judge_model(),
    )
    assert_test(test_case, [metric])


def test_all_metrics_combined():
    """Run the complete metric suite on a single test case.

    Demonstrates how to evaluate multiple dimensions at once. This is the
    pattern you would use in CI to gate on overall agent quality.
    """
    test_case, trace = _build_test_case(dataset.goldens[3])  # Roll 10d6 + stats

    # Trace-enriched variant for step-based metrics
    trace_case = LLMTestCase(
        input=test_case.input,
        actual_output=_trace_as_text(trace),
        expected_output=test_case.expected_output,
        tools_called=test_case.tools_called,
        expected_tools=test_case.expected_tools,
    )

    judge = get_judge_model()
    metrics = [
        TaskCompletionMetric(threshold=0.7, model=judge),
        ToolCorrectnessMetric(threshold=0.8),
        StepEfficiencyMetric(threshold=0.7, model=judge),
        PlanQualityMetric(threshold=0.7, model=judge),
        GEval(
            name="Numerical Presence",
            criteria=(
                "Evaluate whether the output contains ALL THREE of the following: "
                "(1) the individual dice roll results as explicit numbers, "
                "(2) a clearly labeled computed mean value, "
                "(3) a clearly labeled computed standard deviation value. "
                "Score 1.0 if all three are present. "
                "Deduct proportionally for each missing component (0.33 per missing item)."
            ),
            evaluation_params=[
                LLMTestCaseParams.INPUT,
                LLMTestCaseParams.ACTUAL_OUTPUT,
            ],
            threshold=0.75,
            model=judge,
        ),
    ]
    assert_test(trace_case, metrics)
