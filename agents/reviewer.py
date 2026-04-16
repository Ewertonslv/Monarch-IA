import json
import logging
from typing import Any

from agents.base import BaseAgent, SONNET_MODEL
from core.task import Task
from tools.github_tools import GitHubTools

logger = logging.getLogger(__name__)

_SYSTEM = """You are the Code Reviewer Agent for Monarch AI.

You perform a thorough code review of the changes introduced by a pull request.
Focus on: correctness, readability, maintainability, test coverage, and adherence
to best practices.

Respond with a single JSON object:
{
  "confidence": <float 0-1>,
  "approved": <bool>,
  "overall_quality": <str>,   // one of: excellent | good | acceptable | needs_work | rejected
  "comments": [
    {
      "file": <str>,
      "line_hint": <str>,
      "severity": <str>,      // one of: blocking | suggestion | nit
      "comment": <str>
    }
  ],
  "blocking_issues": [<str>, ...],
  "positive_highlights": [<str>, ...],
  "concerns": [<str>, ...]
}"""


class ReviewerAgent(BaseAgent):
    name = "reviewer"
    display_name = "Helena - Revisão"
    model = SONNET_MODEL
    system_prompt = _SYSTEM

    def __init__(self) -> None:
        super().__init__()
        self._github = GitHubTools()

    async def build_user_message(self, task: Task) -> str:
        diff = ""
        if task.pr_url:
            pr_number = int(task.pr_url.rstrip("/").split("/")[-1])
            try:
                diff = self._github.get_pr_diff(pr_number)
            except Exception as exc:
                logger.warning("Could not fetch PR diff: %s", exc)
                diff = "(diff unavailable)"

        return (
            f"Review the following pull request changes.\n\n"
            f"Task: {task.raw_input}\n\n"
            f"PR URL: {task.pr_url or 'N/A'}\n\n"
            f"Diff:\n{diff or '(no diff available)'}"
        )

    async def run(self, task: Task):
        result = await super().run(task)
        task.review_report = result.output
        approved = result.output.get("approved", False)
        task.add_history(
            agent=self.label,
            action="review_complete",
            detail=f"approved={approved} quality={result.output.get('overall_quality')}",
        )
        return result
