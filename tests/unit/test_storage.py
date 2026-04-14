import pytest
import pytest_asyncio
from storage.database import Database
from core.task import Task, TaskStatus


@pytest_asyncio.fixture
async def db(tmp_path):
    url = f"sqlite+aiosqlite:///{tmp_path}/test.db"
    database = Database(url)
    await database.init()
    yield database
    await database.close()


@pytest.mark.asyncio
async def test_save_and_load_task(db):
    task = Task(raw_input="test task")
    await db.save_task(task)
    loaded = await db.get_task(task.task_id)
    assert loaded is not None
    assert loaded.raw_input == "test task"
    assert loaded.status == TaskStatus.PENDING


@pytest.mark.asyncio
async def test_update_task(db):
    task = Task(raw_input="test")
    await db.save_task(task)
    task.status = TaskStatus.RUNNING
    task.add_history(agent="orchestrator", action="started", detail="")
    await db.update_task(task)
    loaded = await db.get_task(task.task_id)
    assert loaded is not None
    assert loaded.status == TaskStatus.RUNNING
    assert len(loaded.history) == 1


@pytest.mark.asyncio
async def test_list_active_tasks(db):
    for i in range(3):
        t = Task(raw_input=f"task {i}")
        await db.save_task(t)
    tasks = await db.list_active_tasks()
    assert len(tasks) == 3


@pytest.mark.asyncio
async def test_done_task_not_in_active(db):
    task = Task(raw_input="completed task")
    await db.save_task(task)
    task.status = TaskStatus.DONE
    await db.update_task(task)
    tasks = await db.list_active_tasks()
    assert all(t.task_id != task.task_id for t in tasks)


@pytest.mark.asyncio
async def test_get_nonexistent_task_returns_none(db):
    result = await db.get_task("monarch-nonexistent")
    assert result is None
