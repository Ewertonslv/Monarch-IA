"""CLI interface for Monarch AI — submit tasks from the terminal."""
import argparse
import asyncio
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


async def _run_cli(raw_input: str) -> None:
    from config import config
    from core.task import Task, TaskStatus
    from core.orchestrator import Orchestrator
    from storage.database import Database

    db = Database(config.database_url)
    await db.init()

    orchestrator = Orchestrator(db)
    task = Task(raw_input=raw_input)

    # For CLI mode, auto-approve both gates
    original_request_approval = orchestrator._request_approval

    async def _auto_approve(task, stage):  # noqa: ANN001
        print(f"\n[AUTO-APPROVE] Stage: {stage} — press Ctrl+C to abort")
        task.status = TaskStatus.RUNNING
        await db.update_task(task)
        return True

    orchestrator._request_approval = _auto_approve  # type: ignore[method-assign]

    print(f"\n🚀 Starting Monarch AI pipeline for: {raw_input}")
    print(f"   Task ID: {task.task_id}\n")

    result = await orchestrator.run(task)

    print(f"\n{'='*60}")
    print(f"Status : {result.status.value.upper()}")
    if result.pr_url:
        print(f"PR URL : {result.pr_url}")
    if result.branch_name:
        print(f"Branch : {result.branch_name}")
    print(f"\nHistory ({len(result.history)} entries):")
    for entry in result.history[-10:]:
        print(f"  {entry.agent:20s} {entry.action:30s} {entry.detail}")
    print(f"{'='*60}\n")

    await db.close()

    sys.exit(0 if result.status.value == "done" else 1)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="monarch",
        description="Monarch AI — Multi-agent SaaS development pipeline",
    )
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Submit a task and run the pipeline")
    run_parser.add_argument("input", nargs="+", help="Feature description")

    args = parser.parse_args()

    if args.command == "run":
        raw_input = " ".join(args.input)
        asyncio.run(_run_cli(raw_input))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
