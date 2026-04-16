from agents.base import BaseAgent, SONNET_MODEL
from core.task import Task

_SYSTEM = """You are the Prioritization Agent for Monarch AI.

Given a task's discovery requirements, assess its business priority and resource
allocation guidance.

Respond with a single JSON object:
{
  "confidence": <float 0-1>,
  "priority": <str>,           // one of: critical | high | medium | low
  "priority_score": <int 1-100>,
  "rationale": <str>,
  "suggested_sprint": <str>,   // e.g. "current" | "next" | "backlog"
  "dependencies": [<str>, ...],
  "risks": [<str>, ...],
  "concerns": [<str>, ...]
}"""


class PrioritizationAgent(BaseAgent):
    name = "prioritization"
    display_name = "Bruno - Prioridade"
    model = SONNET_MODEL
    system_prompt = _SYSTEM

    async def build_user_message(self, task: Task) -> str:
        import json
        reqs = task.requirements or {}
        return (
            f"Assess the priority of this task.\n\n"
            f"Original request: {task.raw_input}\n\n"
            f"Discovery analysis:\n{json.dumps(reqs, indent=2)}"
        )

    async def run(self, task: Task):
        result = await super().run(task)
        task.priority = result.output.get("priority", "medium")
        task.add_history(
            agent=self.label,
            action="prioritization_complete",
            detail=f"priority={task.priority} score={result.output.get('priority_score')}",
        )
        return result
