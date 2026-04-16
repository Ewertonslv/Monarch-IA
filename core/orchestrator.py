import asyncio
import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Callable, Awaitable

from config import config
from core.monarch_core_client import MonarchCoreClient
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
from agents.deploy import DeployAgent
from tools.github_tools import GitHubTools

if TYPE_CHECKING:
    from interfaces.telegram_bot import TelegramBot

logger = logging.getLogger(__name__)

class Orchestrator:
    """Central coordinator — runs the full 11-agent pipeline for a task."""

    def __init__(
        self,
        db: Database,
        progress_callback: Callable[[str, str, dict[str, Any] | None], None] | None = None,
    ) -> None:
        self.db = db
        self._breakers: dict[str, CircuitBreaker] = {}
        self._telegram: "TelegramBot | None" = None
        self._core_client = MonarchCoreClient(
            base_url=config.monarch_core_api_url,
            project_slug=config.monarch_core_project_slug,
            api_key=config.monarch_core_api_key,
        )
        self._progress_callback = progress_callback

    def _report_progress(
        self,
        agent_name: str,
        status: str,
        payload: dict[str, Any] | None = None,
    ) -> None:
        if self._progress_callback:
            try:
                self._progress_callback(agent_name, status, payload)
            except Exception as exc:
                logger.warning("[orchestrator] progress callback failed: %s", exc)

    async def _run_agent(self, agent_name: str, coro_fn: Callable[[], Awaitable[Any]]) -> Any:
        """Run an agent call through its circuit breaker with retry."""
        breaker = self._breaker(agent_name)
        last_exc: Exception | None = None
        for attempt in range(1, config.max_agent_retries + 1):
            self._report_progress(agent_name, "starting", {"attempt": attempt})
            try:
                result = await breaker.call(coro_fn)
                payload: dict[str, Any] = {}
                if hasattr(result, "confidence"):
                    payload["confidence"] = getattr(result, "confidence")
                if hasattr(result, "concerns"):
                    payload["concerns"] = getattr(result, "concerns")
                self._report_progress(agent_name, "finished", payload)
                return result
            except CircuitBreakerError:
                raise
            except Exception as exc:
                last_exc = exc
                self._report_progress(agent_name, "failed", {"error": str(exc), "attempt": attempt})
                logger.warning("[%s] Attempt %d failed: %s", agent_name, attempt, exc)
                if attempt < config.max_agent_retries:
                    await asyncio.sleep(2 ** attempt)
        raise RuntimeError(f"[{agent_name}] All {config.max_agent_retries} retries exhausted") from last_exc

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
        await self._sync_approval_request(task, stage)
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
        timeout_seconds = max(60, config.approval_timeout_minutes * 60)
        for _ in range(timeout_seconds):
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
            await self._sync_approval_decision(task, "approved")
            await self.db.update_task(task)

    async def reject_task(self, task_id: str) -> None:
        task = await self.db.get_task(task_id)
        if task and task.status == TaskStatus.AWAITING_APPROVAL:
            task.status = TaskStatus.DISCARDED
            await self._sync_approval_decision(task, "rejected")
            await self.db.update_task(task)

    # ------------------------------------------------------------------
    # Pipeline
    # ------------------------------------------------------------------

    async def run(self, task: Task) -> Task:
        """Execute the full pipeline for *task*."""
        task.status = TaskStatus.RUNNING
        await self.db.save_task(task)
        await self._sync_task_started(task)
        await self.db.update_task(task)
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
            if config.github_enabled:
                gh = GitHubTools()
                if task.branch_name:
                    try:
                        gh.create_branch(task.branch_name)
                    except Exception as exc:
                        logger.warning("Branch creation failed (may already exist): %s", exc)

            await self._run_agent("implementer", lambda: ImplementerAgent().run(task))

            if config.github_enabled and task.branch_name and not task.pr_url:
                reqs = task.requirements or {}
                task.pr_url = gh.create_pr(
                    title=f"feat: {reqs.get('summary', task.raw_input[:60])}",
                    body=self._build_pr_body(task),
                    head=task.branch_name,
                )
                task.add_history(agent="orchestrator", action="pr_created", detail=task.pr_url)
                await self.db.update_task(task)
            elif not config.github_enabled:
                task.add_history(agent="orchestrator", action="local_mode", detail="GitHub disabled — files written locally")

            await self._run_agent("testing", lambda: TestingAgent().run(task))
            await self._run_agent("reviewer", lambda: ReviewerAgent().run(task))
            await self._run_agent("security", lambda: SecurityAgent().run(task))
            await self._run_agent("deploy", lambda: DeployAgent().run(task))

            security_approved = (task.security_report or {}).get("approved", True)
            review_approved = (task.review_report or {}).get("approved", True)
            if task.pr_url and (not security_approved or not review_approved):
                task.add_history(
                    agent="orchestrator",
                    action="pr_requires_changes",
                    detail=f"review_approved={review_approved} security_approved={security_approved}",
                )

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
            await self._sync_task_final_state(task)

        return task

    async def aclose(self) -> None:
        await self._core_client.aclose()

    async def _sync_task_started(self, task: Task) -> None:
        if not self._core_client.enabled:
            return

        try:
            project = await self._core_client.ensure_project()
            if not project:
                return

            task.core_project_id = project.get("id")
            idea = await self._core_client.create_idea(
                title=f"Pipeline request: {task.raw_input[:80]}",
                raw_input=task.raw_input,
                business_unit_id=project.get("business_unit_id"),
                project_id=task.core_project_id,
            )
            if idea:
                task.core_idea_id = idea.get("id")

            core_task = await self._core_client.create_task(
                project_id=task.core_project_id,
                title=f"[{task.task_id}] {task.raw_input[:120]}",
                description=task.raw_input,
                status="in_progress",
                priority=task.priority or "medium",
                approval_required=False,
            )
            if core_task:
                task.core_task_id = core_task.get("id")
                execution = await self._core_client.create_execution(
                    project_id=task.core_project_id,
                    task_id=task.core_task_id,
                    agent_name="legacy-orchestrator",
                    execution_type="pipeline_run",
                    status="running",
                    input_payload=task.raw_input,
                    started_at=datetime.now(UTC),
                )
                if execution:
                    task.core_execution_id = execution.get("id")
        except Exception as exc:
            logger.warning("[orchestrator] Could not sync start to monarch-core: %s", exc)

    async def _sync_task_final_state(self, task: Task) -> None:
        if not self._core_client.enabled or not task.core_task_id:
            return

        status_map = {
            TaskStatus.PENDING: "todo",
            TaskStatus.RUNNING: "in_progress",
            TaskStatus.AWAITING_APPROVAL: "blocked",
            TaskStatus.DONE: "done",
            TaskStatus.FAILED: "blocked",
            TaskStatus.DISCARDED: "cancelled",
        }

        try:
            await self._core_client.update_task(
                task_id=task.core_task_id,
                status=status_map.get(task.status, "todo"),
                priority=task.priority or "medium",
                approval_required=task.status == TaskStatus.AWAITING_APPROVAL,
            )
            if task.core_execution_id:
                final_status = "completed" if task.status == TaskStatus.DONE else "failed"
                if task.status in (TaskStatus.RUNNING, TaskStatus.AWAITING_APPROVAL):
                    final_status = "running"
                elif task.status == TaskStatus.DISCARDED:
                    final_status = "cancelled"
                await self._core_client.update_execution(
                    execution_id=task.core_execution_id,
                    status=final_status,
                    output_summary=f"Pipeline encerrado com status {task.status.value}",
                    error_message=None if task.status == TaskStatus.DONE else task.history[-1].detail if task.history else None,
                    finished_at=datetime.now(UTC) if final_status in {"completed", "failed", "cancelled"} else None,
                )
        except Exception as exc:
            logger.warning("[orchestrator] Could not sync final state to monarch-core: %s", exc)

    async def _sync_approval_request(self, task: Task, stage: str) -> None:
        if not self._core_client.enabled or not task.core_project_id:
            return

        try:
            if task.core_task_id:
                await self._core_client.update_task(
                    task_id=task.core_task_id,
                    status="blocked",
                    priority=task.priority or "medium",
                    approval_required=True,
                )
            approval = await self._core_client.create_approval(
                project_id=task.core_project_id,
                task_id=task.core_task_id,
                title=f"Aprovar tarefa {task.task_id} em {stage}",
                summary=task.raw_input,
            )
            if approval:
                task.current_core_approval_id = approval.get("id")
            if task.core_project_id:
                await self._core_client.create_execution(
                    project_id=task.core_project_id,
                    task_id=task.core_task_id,
                    agent_name="legacy-orchestrator",
                    execution_type="approval_request",
                    status="waiting",
                    output_summary=f"Aguardando aprovacao em {stage}",
                    started_at=datetime.now(UTC),
                )
        except Exception as exc:
            logger.warning("[orchestrator] Could not create approval in monarch-core: %s", exc)

    async def _sync_approval_decision(self, task: Task, decision: str) -> None:
        if not self._core_client.enabled:
            return

        try:
            if task.current_core_approval_id:
                await self._core_client.decide_approval(
                    approval_id=task.current_core_approval_id,
                    decision=decision,
                )
                task.current_core_approval_id = None

            if task.core_task_id:
                next_status = "in_progress" if decision == "approved" else "cancelled"
                await self._core_client.update_task(
                    task_id=task.core_task_id,
                    status=next_status,
                    priority=task.priority or "medium",
                    approval_required=False,
                )
            if task.core_project_id:
                await self._core_client.create_execution(
                    project_id=task.core_project_id,
                    task_id=task.core_task_id,
                    agent_name="legacy-orchestrator",
                    execution_type="approval_decision",
                    status=decision,
                    output_summary=f"Aprovacao {decision} para a tarefa {task.task_id}",
                    started_at=datetime.now(UTC),
                    finished_at=datetime.now(UTC),
                )
        except Exception as exc:
            logger.warning("[orchestrator] Could not sync approval decision to monarch-core: %s", exc)

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
