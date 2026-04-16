import json
import logging
from typing import Any

from agents.base import BaseAgent, SONNET_MODEL
from config import config
from core.task import Task
from tools.github_tools import GitHubTools
from tools.fs_tools import FsTools

logger = logging.getLogger(__name__)

_SYSTEM = """You are the Implementer Agent for Monarch AI.

You write production-quality Python code following TDD (Red-Green-Refactor).
You have access to GitHub tools to read the existing codebase and write files.

For each implementation step you will:
1. Read relevant existing files to understand context
2. Write the implementation (test file first, then source file)
3. Report what was written

Always respond with a single JSON object:
{
  "confidence": <float 0-1>,
  "files_written": [{"path": <str>, "description": <str>}],
  "summary": <str>,
  "next_step_hint": <str>,
  "concerns": [<str>, ...]
}"""


class ImplementerAgent(BaseAgent):
    name = "implementer"
    model = config.implementer_model or SONNET_MODEL
    max_tokens = config.implementer_max_tokens
    system_prompt = _SYSTEM

    def __init__(self) -> None:
        super().__init__()
        self._github = GitHubTools()
        self._fs = FsTools()

    @property
    def tools(self) -> list[dict[str, Any]]:
        return self._github.as_tools_schema()

    def _trim_text(self, value: Any, limit: int = 400) -> str:
        text = str(value or "").strip()
        if len(text) <= limit:
            return text
        return f"{text[: limit - 3].rstrip()}..."

    def _summarize_architecture(self, arch: dict[str, Any]) -> dict[str, Any]:
        if not arch:
            return {}

        summary: dict[str, Any] = {}
        scalar_keys = (
            "summary",
            "overview",
            "goal",
            "approach",
            "testing_strategy",
            "deployment_notes",
        )
        list_keys = (
            "components",
            "patterns",
            "files_to_modify",
            "new_files",
            "risks",
        )

        for key in scalar_keys:
            if arch.get(key):
                summary[key] = self._trim_text(arch[key], 500)

        for key in list_keys:
            values = arch.get(key)
            if isinstance(values, list) and values:
                summary[key] = [
                    self._trim_text(item, 160) for item in values[:8]
                ]

        if arch.get("data_flow"):
            summary["data_flow"] = self._trim_text(arch["data_flow"], 500)

        return summary

    def _summarize_plan(self, plan: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not plan:
            return []

        summary: list[dict[str, Any]] = []
        for index, step in enumerate(plan[:10], start=1):
            if not isinstance(step, dict):
                summary.append({"step": index, "title": self._trim_text(step, 180)})
                continue

            compact_step = {
                "step": index,
                "title": self._trim_text(
                    step.get("title") or step.get("name") or f"Step {index}",
                    180,
                ),
            }

            if step.get("description"):
                compact_step["description"] = self._trim_text(
                    step["description"], 260
                )
            if step.get("files"):
                compact_step["files"] = [
                    self._trim_text(path, 120) for path in step["files"][:6]
                ]
            if step.get("tests"):
                compact_step["tests"] = self._trim_text(step["tests"], 180)

            summary.append(compact_step)

        return summary

    async def build_user_message(self, task: Task) -> str:
        plan = task.plan or []
        arch = task.architecture or {}
        branch = task.branch_name or "main"
        summarized_arch = self._summarize_architecture(arch)
        summarized_plan = self._summarize_plan(plan)
        return (
            f"Implement the following task on branch '{branch}'.\n\n"
            f"Original request: {task.raw_input}\n\n"
            "Constraints:\n"
            "- Prefer the smallest safe implementation slice first.\n"
            "- Use existing patterns already present in the repository.\n"
            "- Read only the files you need before writing.\n"
            "- Keep changes focused on the requested architecture and plan.\n\n"
            f"Architecture summary:\n{json.dumps(summarized_arch, indent=2)}\n\n"
            f"Implementation plan summary:\n{json.dumps(summarized_plan, indent=2)}\n\n"
            "Use the provided tools to inspect the codebase and write the required files."
        )

    async def execute_tool(self, name: str, inputs: dict[str, Any]) -> Any:
        branch = inputs.pop("branch", None)
        match name:
            case "read_file":
                return self._github.read_file(**inputs)
            case "list_files":
                return self._github.list_files(**inputs)
            case "write_file":
                self._fs.write(inputs["path"], inputs["content"])
                if branch:
                    inputs["branch"] = branch
                self._github.write_file(**inputs)
                return f"Written: {inputs['path']}"
            case "create_branch":
                self._github.create_branch(**inputs)
                return f"Branch created: {inputs['branch_name']}"
            case _:
                raise NotImplementedError(f"Tool not supported: {name}")

    async def run(self, task: Task):
        result = await super().run(task)
        files = result.output.get("files_written", [])
        task.add_history(
            agent=self.name,
            action="implementation_complete",
            detail=f"files_written={len(files)}",
        )
        return result
