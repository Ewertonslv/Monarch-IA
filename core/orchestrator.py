import asyncio
import logging
from typing import TYPE_CHECKING, Any, Callable, Awaitable

from config import config
from core.circuit_breaker import CircuitBreaker, CircuitBreakerError
from core.task import Task, TaskStatus
from storage.database import Database
from agents.discovery import DiscoveryAgent
from agents.prioritization import PrioritizationAgent
from agents.architecture import ArchitectureAgent
from agents.planning import PlanningAgent
from agents.devils_advocate import DevilsAdvocateAgent
from agents.implementer import ImplementerAgent
from agents.testing import TestingAgent
from agents.reviewer import ReviewerAgent
from agents.security import SecurityAgent
from agents.documentation import DocumentationAgent
from agents.observability import ObservabilityAgent
from tools.github_tools import GitHubTools

if TYPE_CHECKING:
    from interfaces.telegram_bot import TelegramBot

logger = logging.getLogger(__name__)

_APPROVAL_TIMEOUT_SECONDS = 300  # 5 minutes


class Orchestrator:
    """Central coordinator — runs the full 11-agent pipeline for a task."""

    def __init__(self, db: Database) -> None:
        self.db = db
        self._breakers: dict[str, CircuitBreaker] = {}
        self._telegram: "TelegramBot | None" = None

    def set_telegram_bot(self, bot: "TelegramBot") -> None:
        """Wire the Telegram bot so approval gates can send notifications."""
        self._telegram = bot

    def _breaker(self, name: str) -> CircuitBreaker:
        if name not in self._breakers:
            self._breakers[name] = CircuitBreaker(
                name=name,
                failure_threshold=config.max_agent_retries,
            )
        return self._breakers[name]

    async def _run_agent(self, agent_name: str, coro_fn: Callable[[], Awaitable[Any]]) -> Any:
        """Run an agent call through its circuit breaker with retry."""
        breaker = self._breaker(agent_name)
        last_exc: Exception | None = None
        for attempt in range(1, config.max_agent_retries + 1):
            try:
                return await breaker.call(coro_fn)
            except CircuitBreakerError:
                raise
            except Exception as exc:
                last_exc = exc
                logger.warning("[%s] Attempt %d failed: %s", agent_name, attempt, exc)
                if attempt < config.max_agent_retries:
                    await asyncio.sleep(2 ** attempt)
        raise RuntimeError(f"[{agent_name}] All {config.max_agent_retries} retries exhausted") from last_exc

    # ------------------------------------------------------------------
    # Human-approval gate
    # ------------------------------------------------------------------

    async def _request_approval(self, task: Task, stage: str) -> bool:
        """Update task to awaiting_approval, notify via Telegram, then wait.

        Resolved externally by Telegram inline buttons or web panel buttons
        calling approve_task() / reject_task(). Times out after 5 minutes.
        """
        task.status = TaskStatus.AWAITING_APPROVAL
        task.add_history(agent="orchestrator", action="awaiting_approval", detail=stage)
        await self.db.update_task(task)
        logger.info("[orchestrator] Task %s awaiting approval at stage: %s", task.task_id, stage)

        # Send Telegram notification with approve/reject buttons
        if self._telegram:
            reqs = task.requirements or {}
            summary = reqs.get("summary", task.raw_input[:80])
            try:
                await self._telegram.send_approval_request(
                    task_id=task.task_id,
                    stage=stage,
                    summary=summary,
                )
            except Exception as exc:
                logger.warning("[orchestrator] Could not send Telegram approval: %s", exc)

        # Poll DB until status changes (resolved by bot/web) or timeout
        for _ in range(_APPROVAL_TIMEOUT_SECONDS):
            await asyncio.sleep(1)
            fresh = await self.db.get_task(task.task_id)
            if fresh and fresh.status != TaskStatus.AWAITING_APPROVAL:
                task.status = fresh.status
                return fresh.status not in (TaskStatus.FAILED, TaskStatus.DISCARDED)

        # Timeout — treat as rejected
        task.status = TaskStatus.FAILED
        task.add_history(agent="orchestrator", action="approval_timeout", detail=stage)
        return False

    async def approve_task(self, task_id: str) -> None:
        task = await self.db.get_task(task_id)
        if task and task.status == TaskStatus.AWAITING_APPROVAL:
            task.status = TaskStatus.RUNNING
            await self.db.update_task(task)

    async def reject_task(self, task_id: str) -> None:
        task = await self.db.get_task(task_id)
        if task and task.status == TaskStatus.AWAITING_APPROVAL:
            task.status = TaskStatus.DISCARDED
            await self.db.update_task(task)

    # ------------------------------------------------------------------
    # Pipeline
    # ------------------------------------------------------------------

    async def run(self, task: Task) -> Task:
        """Execute the full pipeline for *task*."""
        task.status = TaskStatus.RUNNING
        await self.db.save_task(task)
        logger.info("[orchestrator] Starting pipeline for %s", task.task_id)

        try:
            # --- Direction layer ---
            await self._run_agent("discovery", lambda: DiscoveryAgent().run(task))

            # --- Definition layer ---
            await self._run_agent("prioritization", lambda: PrioritizationAgent().run(task))
            await self._run_agent("architecture", lambda: ArchitectureAgent().run(task))
            await self._run_agent("planning", lambda: PlanningAgent().run(task))

            # Devil's Advocate — up to 2 rounds
            for round_num in range(2):
                result = await self._run_agent(
                    "devils_advocate", lambda: DevilsAdvocateAgent().run(task)
                )
                if result.output.get("approved", False):
                    break
                must_fix = result.output.get("must_fix_before_implementation", [])
                if must_fix:
                    # Update the plan context with the issues so the next agents see them
                    task.add_history(
                        agent="orchestrator",
                        action="devils_advocate_revision",
                        detail=f"round={round_num + 1} issues={len(must_fix)}",
                    )
                    if round_num == 0:
                        # Ask Architecture + Planning to revise
                        await self._run_agent("architecture", lambda: ArchitectureAgent().run(task))
                        await self._run_agent("planning", lambda: PlanningAgent().run(task))

            # --- Human approval gate (post-planning) ---
            approved = await self._request_approval(task, "post_planning")
            if not approved:
                task.status = TaskStatus.DISCARDED
                task.add_history(agent="orchestrator", action="rejected", detail="post_planning")
                logger.info("[orchestrator] Task %s rejected at post-planning", task.task_id)
                return task

            # --- Execution layer ---
            task.status = TaskStatus.RUNNING
            gh = GitHubTools()
            if task.branch_name:
                try:
                    gh.create_branch(task.branch_name)
                except Exception as exc:
                    logger.warning("Branch creation failed (may already exist): %s", exc)

            await self._run_agent("implementer", lambda: ImplementerAgent().run(task))
            await self._run_agent("testing", lambda: TestingAgent().run(task))
            await self._run_agent("reviewer", lambda: ReviewerAgent().run(task))
            await self._run_agent("security", lambda: SecurityAgent().run(task))

            # Create PR if branch was made and no blocking issues
            security_approved = (task.security_report or {}).get("approved", True)
            review_approved = (task.review_report or {}).get("approved", True)

            if task.branch_name and security_approved and review_approved:
                reqs = task.requirements or {}
                pr_url = gh.create_pr(
                    title=f"feat: {reqs.get('summary', task.raw_input[:60])}",
                    body=self._build_pr_body(task),
                    head=task.branch_name,
                )
                task.pr_url = pr_url
                task.add_history(agent="orchestrator", action="pr_created", detail=pr_url)

            # --- Human approval gate (post-implementation) ---
            approved = await self._request_approval(task, "post_implementation")
            if not approved:
                task.status = TaskStatus.DISCARDED
                task.add_history(agent="orchestrator", action="rejected", detail="post_implementation")
                return task

            # --- Support layer ---
            task.status = TaskStatus.RUNNING
            await self._run_agent("documentation", lambda: DocumentationAgent().run(task))
            await self._run_agent("observability", lambda: ObservabilityAgent().run(task))

            task.status = TaskStatus.DONE
            task.add_history(agent="orchestrator", action="pipeline_complete", detail="")
            logger.info("[orchestrator] Pipeline complete for %s", task.task_id)

        except CircuitBreakerError as exc:
            task.status = TaskStatus.FAILED
            task.add_history(agent="orchestrator", action="circuit_breaker_open", detail=str(exc))
            logger.error("[orchestrator] Circuit breaker blocked task %s: %s", task.task_id, exc)
        except Exception as exc:
            task.status = TaskStatus.FAILED
            task.add_history(agent="orchestrator", action="pipeline_error", detail=str(exc))
            logger.exception("[orchestrator] Pipeline failed for %s", task.task_id)
        finally:
            await self.db.update_task(task)

        return task

    def _build_pr_body(self, task: Task) -> str:
        reqs = task.requirements or {}
        lines = [
            f"## Summary",
            f"{reqs.get('summary', task.raw_input)}",
            "",
            f"## Complexity",
            f"`{reqs.get('complexity', 'unknown')}`",
            "",
            f"## Affected Areas",
        ]
        for area in reqs.get("affected_areas", []):
            lines.append(f"- {area}")
        lines += [
            "",
            "## Acceptance Criteria",
        ]
        for criterion in reqs.get("acceptance_criteria", []):
            lines.append(f"- [ ] {criterion}")
        lines += [
            "",
            "---",
            "_Generated by [Monarch AI](https://github.com/monarch-ai)_",
        ]
        return "\n".join(lines)
