# Agent Evaluations with DeepEval

Evaluate the multi-agent supervisor (dice roller + stats) using [DeepEval](https://github.com/confident-ai/deepeval). The tutorial covers the full evaluation workflow: golden dataset, agent trace capture, and five metrics — including a custom one.

## Concepts

- **Golden dataset**: fixed inputs with expected outputs and expected tool call sequences
- **Agent trace**: the full record of tool calls, results, and final response captured from a live agent run
- **LLM-as-judge**: an LLM evaluates soft criteria (task completion, plan quality) that rule-based checks cannot
- **DeepEval metrics**: pytest-compatible metrics that fail the test when the score falls below a threshold

## Metrics covered

| Test | Metric | What it checks |
|---|---|---|
| `test_task_completion` | `TaskCompletionMetric` | Did the final response fully solve the user's request? |
| `test_tool_correctness` | `ToolCorrectnessMetric` | Did the agent call the right sub-agents in the right order? |
| `test_step_efficiency` | `StepEfficiencyMetric` | Were there unnecessary or redundant tool calls? |
| `test_plan_quality` | `PlanQualityMetric` | Was the orchestration plan reasonable before execution began? |
| `test_custom_metric_numerical_presence` | `GEval` (custom) | Does the output contain roll values, mean, and std dev? |
| `test_all_metrics_combined` | All of the above | Full suite on one test case — the CI gate pattern |

## Setup

Install the eval dependencies alongside the ADK ones:

```bash
uv sync --extra adk --extra eval
```

### Gemini (default)

```bash
export GOOGLE_API_KEY="your-gemini-api-key"
```

### Groq

```bash
export MODEL_PROVIDER=groq
export GROQ_API_KEY="your-groq-api-key"
```

### Vertex AI

One-time auth on your machine:

```bash
gcloud auth application-default login
```

Then configure the provider:

```bash
export MODEL_PROVIDER=vertex
export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
export GOOGLE_CLOUD_LOCATION="global"
# optional
export VERTEX_MODEL="gemini-2.5-flash-lite"
```

The judge model reads the same provider env vars as the agent itself (`MODEL_PROVIDER`, plus `GEMINI_MODEL` / `GROQ_MODEL` / `VERTEX_MODEL` depending on provider).

## Run

```bash
uv run pytest src/tutorials/t07_evaluations/ -v
```

Run a single metric:

```bash
uv run pytest src/tutorials/t07_evaluations/test_evals.py::test_task_completion -v
```

## How it works

### 1. Agent runner (`agent_runner.py`)

Executes the supervisor agent in-process via `InMemoryRunner` and captures:

- `final_response` — the last text the supervisor emits
- `tools_called` — ordered list of every tool/sub-agent invoked (e.g. `["roll_die_agent", "stats_agent"]`)
- `steps` — human-readable trace of each action for trace-based metrics

### 2. Golden dataset (`dataset.py`)

Four representative cases stored as DeepEval `Golden` objects inside an `EvaluationDataset`. Each `Golden` uses native DeepEval fields:

- `input` — the user query
- `expected_output` — what a correct response must contain
- `expected_tools` — ordered `ToolCall` sequence the supervisor should invoke
- `additional_metadata` — arbitrary dict (used here for `task_description`)

Because the dataset is an `EvaluationDataset`, it can be pushed to Confident AI and pulled back later with two lines:

```python
dataset.push(alias="supervisor-evals")   # upload once
dataset.pull(alias="supervisor-evals")   # restore anywhere
```

### 3. Judge model (`judge_model.py`)

A thin `DeepEvalBaseLLM` wrapper around LiteLLM (already installed via `google-adk`). Mirrors `model_config.py`'s env var conventions so the same provider is used for both the agent and the judge.

### 4. Test file (`test_evals.py`)

Each test function:
1. Picks a golden case from the dataset
2. Runs the agent live via `agent_runner.run_agent()`
3. Constructs an `LLMTestCase` from the trace
4. Calls `assert_test()` — passes if all metric scores meet their thresholds

For step-based metrics (`StepEfficiencyMetric`, `PlanQualityMetric`), the full numbered trace is passed as `actual_output` so the judge can inspect each step.

## Extending the golden dataset

Add `Golden` entries directly in `dataset.py`:

```python
from deepeval.dataset import Golden
from deepeval.test_case import ToolCall

Golden(
    input="your user query",
    expected_output="what a correct answer must contain",
    expected_tools=[ToolCall(name="tool_a"), ToolCall(name="tool_b")],
    additional_metadata={"task_description": "short label"},
)
```

## Adding your own metrics

### Custom GEval metric

```python
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams

sql_safety = GEval(
    name="SQL Safety",
    criteria=(
        "Check that the SQL query in the response is read-only: "
        "it must not contain INSERT, UPDATE, DELETE, DROP, or TRUNCATE."
    ),
    evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
    threshold=1.0,
    model=get_judge_model(),
)
```
