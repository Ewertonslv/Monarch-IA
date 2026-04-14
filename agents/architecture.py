from agents.base import BaseAgent, OPUS_MODEL
from core.task import Task

_SYSTEM = """You are the Architecture Agent for Monarch AI.

You design the technical solution for a feature request. You have access to the
repository structure to understand the existing codebase before proposing changes.

Respond with a single JSON object:
{
  "confidence": <float 0-1>,
  "approach": <str>,                    // high-level description of the solution
  "new_files": [<str>, ...],            // files to be created
  "modified_files": [<str>, ...],       // existing files to be changed
  "deleted_files": [<str>, ...],
  "database_changes": [<str>, ...],     // migrations or schema changes
  "api_endpoints": [                    // only for API features
    {"method": <str>, "path": <str>, "description": <str>}
  ],
  "test_strategy": <str>,               // unit | integration | e2e or combination
  "patterns": [<str>, ...],             // design patterns to apply
  "concerns": [<str>, ...]
}"""


class ArchitectureAgent(BaseAgent):
    name = "architecture"
    model = OPUS_MODEL
    system_prompt = _SYSTEM

    async def build_user_message(self, task: Task) -> str:
        import json
        reqs = task.requirements or {}
        return (
            f"Design the technical architecture for this task.\n\n"
            f"Original request: {task.raw_input}\n\n"
            f"Requirements:\n{json.dumps(reqs, indent=2)}\n\n"
            f"Priority: {task.priority or 'unknown'}"
        )

    async def run(self, task: Task):
        result = await super().run(task)
        task.architecture = result.output
        task.add_history(
            agent=self.name,
            action="architecture_complete",
            detail=f"new_files={len(result.output.get('new_files', []))} modified={len(result.output.get('modified_files', []))}",
        )
        return result
