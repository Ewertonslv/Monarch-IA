from agents.base import BaseAgent, SONNET_MODEL
from core.task import Task

_SYSTEM = """You are the Discovery Agent for Monarch AI — a multi-agent system that
automates SaaS software development.

Your job is to deeply understand a raw feature request or task description and
produce a structured analysis that the rest of the pipeline (Planning, Architecture,
Implementation) will rely on.

Always respond with a single JSON object (no markdown code fences) with these fields:
{
  "confidence": <float 0-1>,        // how confident you are in the interpretation
  "summary": <str>,                 // one-sentence plain-language summary
  "feature_type": <str>,            // one of: backend_api | frontend | fullstack | refactor | bugfix | infrastructure | enhancement | other
  "complexity": <str>,              // one of: trivial | low | medium | high | critical
  "affected_areas": [<str>, ...],   // modules / domains likely to be changed
  "acceptance_criteria": [<str>, ...],  // testable done conditions
  "out_of_scope": [<str>, ...],     // things explicitly NOT included
  "concerns": [<str>, ...]          // ambiguities, risks, or questions needing clarification
}"""


class DiscoveryAgent(BaseAgent):
    name = "discovery"
    display_name = "Alice - Descoberta"
    model = SONNET_MODEL
    system_prompt = _SYSTEM

    async def build_user_message(self, task: Task) -> str:
        return (
            f"Analyze the following feature request and return a structured JSON analysis.\n\n"
            f"Feature request:\n{task.raw_input}"
        )

    async def run(self, task: Task):
        result = await super().run(task)
        # Persist the structured requirements back onto the task
        task.requirements = result.output
        task.add_history(
            agent=self.label,
            action="discovery_complete",
            detail=f"complexity={result.output.get('complexity')} confidence={result.confidence:.2f}",
        )
        return result
