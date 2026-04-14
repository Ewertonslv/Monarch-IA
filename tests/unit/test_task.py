from core.task import HistoryEntry, Task, TaskStatus


def test_task_creation():
    task = Task(raw_input="Criar endpoint /users/{id}")
    assert task.task_id.startswith("monarch-")
    assert task.status == TaskStatus.PENDING
    assert task.raw_input == "Criar endpoint /users/{id}"
    assert task.history == []


def test_task_add_history():
    task = Task(raw_input="test")
    task.add_history(agent="discovery", action="started", detail="processing input")
    assert len(task.history) == 1
    assert task.history[0].agent == "discovery"
    assert task.history[0].action == "started"


def test_task_status_transition():
    task = Task(raw_input="test")
    task.status = TaskStatus.RUNNING
    assert task.status == TaskStatus.RUNNING


def test_task_ids_are_unique():
    t1 = Task(raw_input="a")
    t2 = Task(raw_input="b")
    assert t1.task_id != t2.task_id
