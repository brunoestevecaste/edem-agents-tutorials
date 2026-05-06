"""Golden dataset for the multi-agent supervisor evaluation.

Uses DeepEval's Golden and EvaluationDataset so the dataset can be extended
with push/pull to Confident AI when needed.
"""

from deepeval.dataset import EvaluationDataset, Golden
from deepeval.test_case import ToolCall

dataset = EvaluationDataset(
    goldens=[
        Golden(
            input="Roll a 6-sided die 5 times and give me the stats",
            expected_output=(
                "The response must include: the 5 individual dice roll results (integers 1–6), "
                "the computed mean of those rolls, and the computed standard deviation."
            ),
            expected_tools=[
                ToolCall(name="roll_die_agent"),
                ToolCall(name="stats_agent"),
            ],
            additional_metadata={
                "task_description": "Roll 5d6 and compute mean and standard deviation"
            },
        ),
        Golden(
            input="Roll a 20-sided die 3 times, then compute mean and standard deviation",
            expected_output=(
                "The response must include: 3 roll results (integers 1–20), "
                "the computed mean, and the computed standard deviation."
            ),
            expected_tools=[
                ToolCall(name="roll_die_agent"),
                ToolCall(name="stats_agent"),
            ],
            additional_metadata={
                "task_description": "Roll 3d20 and compute statistics"
            },
        ),
        Golden(
            input="Roll a die once and tell me the result",
            expected_output=(
                "The response must include a single dice roll result (integer 1–6)."
            ),
            expected_tools=[
                ToolCall(name="roll_die_agent"),
            ],
            additional_metadata={"task_description": "Roll a single 6-sided die"},
        ),
        Golden(
            input="Roll a 6-sided die 10 times and give me the statistics",
            expected_output=(
                "The response must include: 10 roll results (integers 1–6), "
                "the computed mean, and the computed standard deviation."
            ),
            expected_tools=[
                ToolCall(name="roll_die_agent"),
                ToolCall(name="stats_agent"),
            ],
            additional_metadata={
                "task_description": "Roll 10d6 and compute statistics"
            },
        ),
    ]
)
