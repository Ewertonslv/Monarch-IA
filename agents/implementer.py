import json
import logging
from typing import Any

from agents.base import BaseAgent, OPUS_MODEL
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
    model = OPUS_MODEL
    system_prompt = _SYSTEM

    def __init__(self) -> None:
        super().__init__()
        self._github = GitHubTools()
        self._fs = FsTools()

    @property
    def tools(self) -> list[dict[str, Any]]:
        return self._github.as_tools_schema()

    async def build_user_message(self, task: Task) -> str:
        plan = task.plan or []
        arch = task.architecture or {}
        branch = task.branch_name or "main"
        return (
            f"Implement the following task on branch '{branch}'.\n\n"
            f"Original request: {task.raw_input}\n\n"
            f"Architecture:\n{json.dumps(arch, indent=2)}\n\n"
            f"Implementation plan:\n{json.dumps(plan, indent=2)}\n\n"
            f"Use the provided tools to read existing files and write new ones."
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
