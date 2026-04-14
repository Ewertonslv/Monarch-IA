import json
import logging
from typing import Any

from agents.base import BaseAgent, OPUS_MODEL
from core.task import Task

logger = logging.getLogger(__name__)

_SYSTEM = """You are the Security Agent for Monarch AI.

You perform a security review of code changes, focusing on OWASP Top 10 and common
vulnerability classes: injection, authentication flaws, sensitive data exposure,
broken access control, insecure deserialization, and more.

Respond with a single JSON object:
{
  "confidence": <float 0-1>,
  "approved": <bool>,
  "risk_level": <str>,        // one of: none | low | medium | high | critical
  "vulnerabilities": [
    {
      "cwe": <str>,           // e.g. "CWE-89 SQL Injection"
      "severity": <str>,      // critical | high | medium | low | info
      "location": <str>,
      "description": <str>,
      "remediation": <str>
    }
  ],
  "blocking_vulnerabilities": [<str>, ...],
  "security_positives": [<str>, ...],
  "concerns": [<str>, ...]
}"""


class SecurityAgent(BaseAgent):
    name = "security"
    model = OPUS_MODEL
    system_prompt = _SYSTEM

    async def build_user_message(self, task: Task) -> str:
        review = task.review_report or {}
        test_results = task.test_results or {}
        return (
            f"Perform a security review for the following task.\n\n"
            f"Task: {task.raw_input}\n\n"
            f"Architecture: {json.dumps(task.architecture or {}, indent=2)}\n\n"
            f"Code review report:\n{json.dumps(review, indent=2)}\n\n"
            f"Test results:\n{json.dumps(test_results, indent=2)}"
        )

    async def run(self, task: Task):
        result = await super().run(task)
        task.security_report = result.output
        approved = result.output.get("approved", False)
        risk = result.output.get("risk_level", "unknown")
        task.add_history(
            agent=self.name,
            action="security_review_complete",
            detail=f"approved={approved} risk={risk}",
        )
        return result
