import json
from dataclasses import asdict
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.task import HistoryEntry, Task, TaskMode, TaskStatus
from storage.models import Base, TaskRecord


def _serialize_task(task: Task) -> str:
    def default(obj: object) -> str:
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, TaskStatus):
            return obj.value
        if isinstance(obj, TaskMode):
            return obj.value
        raise TypeError(f"Not serializable: {type(obj)}")

    return json.dumps(asdict(task), default=default)


def _deserialize_task(data: str) -> Task:
    raw = json.loads(data)
    raw["mode"] = TaskMode(raw.get("mode", TaskMode.EXECUTION.value))
    raw["status"] = TaskStatus(raw["status"])
    raw["history"] = [
        HistoryEntry(
            agent=h["agent"],
            action=h["action"],
            detail=h["detail"],
            timestamp=datetime.fromisoformat(h["timestamp"]),
        )
        for h in raw.get("history", [])
    ]
    for dt_field in ("created_at", "updated_at"):
        if raw.get(dt_field):
            raw[dt_field] = datetime.fromisoformat(raw[dt_field])
    return Task(**raw)


class Database:
    def __init__(self, url: str) -> None:
        self._engine = create_async_engine(url)
        self._session_factory = async_sessionmaker(self._engine, expire_on_commit=False)

    async def init(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def close(self) -> None:
        await self._engine.dispose()

    async def save_task(self, task: Task) -> None:
        async with self._session_factory() as session:
            record = TaskRecord(
                task_id=task.task_id,
                status=task.status.value,
                raw_input=task.raw_input,
                context_json=_serialize_task(task),
            )
            session.add(record)
            await session.commit()

    async def update_task(self, task: Task) -> None:
        async with self._session_factory() as session:
            record = await session.get(TaskRecord, task.task_id)
            if record:
                record.status = task.status.value
                record.context_json = _serialize_task(task)
                await session.commit()

    async def get_task(self, task_id: str) -> Task | None:
        async with self._session_factory() as session:
            record = await session.get(TaskRecord, task_id)
            if record is None:
                return None
            return _deserialize_task(record.context_json)

    async def list_active_tasks(self) -> list[Task]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(TaskRecord).where(
                    TaskRecord.status.notin_(["done", "failed", "discarded"])
                )
            )
            return [_deserialize_task(r.context_json) for r in result.scalars()]
