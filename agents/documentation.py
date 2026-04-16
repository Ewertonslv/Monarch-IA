import json
import logging
from typing import Any

from agents.base import BaseAgent, SONNET_MODEL
from core.task import Task
from tools.github_tools import GitHubTools

logger = logging.getLogger(__name__)

_SYSTEM = """You are the Documentation Agent for Monarch AI.

You generate and update documentation for code changes: docstrings, README sections,
API docs, and CHANGELOG entries.

Respond with a single JSON object:
{
  "confidence": <float 0-1>,
  "changelog_entry": <str>,         // Markdown changelog entry
  "readme_sections": [              // sections to add/update in README
    {"heading": <str>, "content": <str>}
  ],
  "api_docs": [                     // for API endpoints
    {"endpoint": <str>, "description": <str>, "example": <str>}
  ],
  "inline_docs": [                  // docstrings/comments suggestions
    {"file": <str>, "suggestion": <str>}
  ],
  "concerns": [<str>, ...]
}"""


class DocumentationAgent(BaseAgent):
    name = "documentation"
    display_name = "Karla - Documentação"
    model = SONNET_MODEL
    system_prompt = _SYSTEM

    def __init__(self) -> None:
        super().__init__()
        self._github = GitHubTools()

    async def build_user_message(self, task: Task) -> str:
        arch = task.architecture or {}
        review = task.review_report or {}
        return (
            f"Generate documentation for the following completed task.\n\n"
            f"Task: {task.raw_input}\n\n"
            f"Architecture:\n{json.dumps(arch, indent=2)}\n\n"
            f"Review summary:\n{json.dumps(review, indent=2)}\n\n"
            f"PR URL: {task.pr_url or 'N/A'}"
        )

    async def run(self, task: Task):
        result = await super().run(task)
        task.add_history(
            agent=self.label,
            action="documentation_complete",
            detail=f"changelog_entry={'yes' if result.output.get('changelog_entry') else 'no'}",
        )
        return result
