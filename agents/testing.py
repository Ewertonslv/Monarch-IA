import json
import logging
from typing import Any

from agents.base import BaseAgent, SONNET_MODEL
from core.task import Task
from tools.code_tools import CodeTools

logger = logging.getLogger(__name__)

_SYSTEM = """You are the Testing Agent for Monarch AI.

You analyse test results from pytest, ruff, mypy, and bandit, then produce a
structured quality report.

Respond with a single JSON object:
{
  "confidence": <float 0-1>,
  "all_passed": <bool>,
  "pytest": {"passed": <bool>, "summary": <str>},
  "ruff": {"passed": <bool>, "issue_count": <int>},
  "mypy": {"passed": <bool>, "summary": <str>},
  "bandit": {"passed": <bool>, "high_severity": <int>},
  "blocking_issues": [<str>, ...],
  "recommendations": [<str>, ...],
  "concerns": [<str>, ...]
}"""


class TestingAgent(BaseAgent):
    name = "testing"
    display_name = "Gabriel - Testes"
    model = SONNET_MODEL
    system_prompt = _SYSTEM

    def __init__(self, workdir: str = ".") -> None:
        super().__init__()
        self._code_tools = CodeTools(workdir=workdir)

    async def build_user_message(self, task: Task) -> str:
        checks = self._code_tools.run_all_checks()
        return (
            f"Analyse these quality check results for the task:\n"
            f"Task: {task.raw_input}\n\n"
            f"Results:\n{json.dumps(checks, indent=2)}"
        )

    async def run(self, task: Task):
        result = await super().run(task)
        task.test_results = result.output
        all_passed = result.output.get("all_passed", False)
        task.add_history(
            agent=self.label,
            action="testing_complete",
            detail=f"all_passed={all_passed}",
        )
        return result
