from agents.base import BaseAgent, OPUS_MODEL
from core.task import Task

_SYSTEM = """You are the Devil's Advocate Agent for Monarch AI.

Your role is to critically challenge the proposed plan and architecture, identifying
flaws, risks, edge cases, and blind spots BEFORE implementation begins.

Be specific and actionable — for each issue, suggest a concrete fix or mitigation.

Respond with a single JSON object:
{
  "confidence": <float 0-1>,    // confidence that the plan is sound (higher = fewer issues)
  "approved": <bool>,           // true if the plan is safe to proceed
  "issues": [
    {
      "severity": <str>,        // one of: critical | high | medium | low
      "category": <str>,        // e.g. security | correctness | performance | maintainability | testing
      "description": <str>,
      "suggestion": <str>
    }
  ],
  "must_fix_before_implementation": [<str>, ...],  // descriptions of blocking issues
  "nice_to_have": [<str>, ...],
  "concerns": [<str>, ...]
}"""


class DevilsAdvocateAgent(BaseAgent):
    name = "devils_advocate"
    model = OPUS_MODEL
    system_prompt = _SYSTEM

    async def build_user_message(self, task: Task) -> str:
        import json
        plan = task.plan or []
        arch = task.architecture or {}
        reqs = task.requirements or {}
        return (
            f"Critically review this implementation plan.\n\n"
            f"Original request: {task.raw_input}\n\n"
            f"Requirements:\n{json.dumps(reqs, indent=2)}\n\n"
            f"Architecture:\n{json.dumps(arch, indent=2)}\n\n"
            f"Implementation plan:\n{json.dumps(plan, indent=2)}"
        )

    async def run(self, task: Task):
        result = await super().run(task)
        task.devils_advocate_rounds.append(result.output)
        approved = result.output.get("approved", False)
        issues_count = len(result.output.get("issues", []))
        task.add_history(
            agent=self.name,
            action="review_complete",
            detail=f"approved={approved} issues={issues_count}",
        )
        return result
