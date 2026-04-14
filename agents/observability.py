import json
import logging
from typing import Any

from agents.base import BaseAgent, HAIKU_MODEL
from core.task import Task

logger = logging.getLogger(__name__)

_SYSTEM = """You are the Observability Agent for Monarch AI.

You recommend logging, metrics, alerting, and tracing instrumentation for code
changes. Your goal is to ensure the feature is observable in production.

Respond with a single JSON object:
{
  "confidence": <float 0-1>,
  "logging_recommendations": [<str>, ...],
  "metrics_to_add": [
    {"name": <str>, "type": <str>, "description": <str>}
  ],
  "alerts_to_configure": [
    {"name": <str>, "condition": <str>, "severity": <str>}
  ],
  "tracing_spans": [<str>, ...],
  "health_check_suggestions": [<str>, ...],
  "concerns": [<str>, ...]
}"""


class ObservabilityAgent(BaseAgent):
    name = "observability"
    model = HAIKU_MODEL
    system_prompt = _SYSTEM

    async def build_user_message(self, task: Task) -> str:
        arch = task.architecture or {}
        return (
            f"Recommend observability instrumentation for the following task.\n\n"
            f"Task: {task.raw_input}\n\n"
            f"Architecture:\n{json.dumps(arch, indent=2)}\n\n"
            f"Feature type: {(task.requirements or {}).get('feature_type', 'unknown')}\n"
            f"Affected areas: {(task.requirements or {}).get('affected_areas', [])}"
        )

    async def run(self, task: Task):
        result = await super().run(task)
        metrics_count = len(result.output.get("metrics_to_add", []))
        task.add_history(
            agent=self.name,
            action="observability_complete",
            detail=f"metrics={metrics_count} alerts={len(result.output.get('alerts_to_configure', []))}",
        )
        return result
