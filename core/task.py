import uuid
from dataclasses import dataclass, field
from datetime import datetime, UTC
from enum import Enum
from typing import Any


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    AWAITING_APPROVAL = "awaiting_approval"
    DONE = "done"
    FAILED = "failed"
    DISCARDED = "discarded"


@dataclass
class HistoryEntry:
    agent: str
    action: str
    detail: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class Task:
    raw_input: str
    task_id: str = field(default_factory=lambda: f"monarch-{uuid.uuid4().hex[:8]}")
    status: TaskStatus = TaskStatus.PENDING
    requirements: dict[str, Any] | None = None
    priority: str | None = None
    architecture: dict[str, Any] | None = None
    plan: list[dict[str, Any]] | None = None
    devils_advocate_rounds: list[dict[str, Any]] = field(default_factory=list)
    branch_name: str | None = None
    pr_url: str | None = None
    test_results: dict[str, Any] | None = None
    review_report: dict[str, Any] | None = None
    security_report: dict[str, Any] | None = None
    history: list[HistoryEntry] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def add_history(self, agent: str, action: str, detail: str) -> None:
        self.history.append(HistoryEntry(agent=agent, action=action, detail=detail))
        self.updated_at = datetime.now(UTC)
