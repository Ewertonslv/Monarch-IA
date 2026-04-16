from agents.base import BaseAgent, SONNET_MODEL
from core.task import Task

_SYSTEM = """You are the Planning Agent for Monarch AI.

You convert an architecture design into a precise, ordered implementation plan — a
sequence of atomic steps that the Implementer Agent will execute one by one.

Each step must be self-contained and independently executable.

Respond with a single JSON object:
{
  "confidence": <float 0-1>,
  "steps": [
    {
      "id": <int>,
      "title": <str>,
      "description": <str>,
      "type": <str>,          // one of: write_test | write_code | modify_code | create_file | run_command | create_migration
      "files": [<str>, ...],  // files this step touches
      "dependencies": [<int>, ...],  // step IDs this step depends on
      "acceptance": <str>     // how to verify this step is done
    }
  ],
  "branch_name": <str>,       // suggested git branch name e.g. "feat/login-endpoint"
  "estimated_steps": <int>,
  "concerns": [<str>, ...]
}"""


class PlanningAgent(BaseAgent):
    name = "planning"
    display_name = "Diego - Planejamento"
    model = SONNET_MODEL
    system_prompt = _SYSTEM

    async def build_user_message(self, task: Task) -> str:
        import json
        arch = task.architecture or {}
        reqs = task.requirements or {}
        return (
            f"Create a step-by-step implementation plan.\n\n"
            f"Original request: {task.raw_input}\n\n"
            f"Requirements:\n{json.dumps(reqs, indent=2)}\n\n"
            f"Architecture:\n{json.dumps(arch, indent=2)}"
        )

    async def run(self, task: Task):
        result = await super().run(task)
        task.plan = result.output.get("steps", [])
        if result.output.get("branch_name"):
            task.branch_name = result.output["branch_name"]
        task.add_history(
            agent=self.label,
            action="planning_complete",
            detail=f"steps={len(task.plan)} branch={task.branch_name}",
        )
        return result
