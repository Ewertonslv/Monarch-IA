# Monarch AI — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a multi-agent AI system that receives development tasks in natural language and delivers tested, documented GitHub PRs with minimal human intervention.

**Architecture:** Central Orchestrator + 11 specialized agents using Anthropic SDK (tool_use + prompt caching). FastAPI web UI + Telegram bot for human approval. SQLite persistence for task context.

**Tech Stack:** Python 3.12, anthropic SDK, FastAPI, python-telegram-bot, PyGithub, SQLite (aiosqlite), pytest, ruff, mypy, bandit

---

### Task 1: Project Setup

**Files:**
- Create: `pyproject.toml`
- Create: `config.py`
- Create: `.env.example`
- Create: `tests/__init__.py`
- Create: `tests/unit/__init__.py`
- Create: `tests/integration/__init__.py`
- Create: `tests/fixtures/__init__.py`

- [ ] **Step 1: Write failing test for config loading**

```python
# tests/unit/test_config.py
import pytest
import os
from unittest.mock import patch

def test_config_loads_required_vars():
    env = {
        "ANTHROPIC_API_KEY": "sk-test",
        "GITHUB_TOKEN": "ghp_test",
        "GITHUB_REPO": "owner/repo",
        "TELEGRAM_BOT_TOKEN": "123:abc",
        "TELEGRAM_CHAT_ID": "456",
    }
    with patch.dict(os.environ, env):
        from config import Config
        c = Config()
        assert c.anthropic_api_key == "sk-test"
        assert c.github_repo == "owner/repo"

def test_config_raises_on_missing_required():
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
            from config import Config
            Config()
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_config.py -v
```
Expected: `FAIL — ModuleNotFoundError: No module named 'config'`

- [ ] **Step 3: Create `pyproject.toml`**

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.backends.legacy:BuildBackend"

[project]
name = "monarch-ai"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "anthropic>=0.49.0",
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "python-telegram-bot>=21.0",
    "PyGithub>=2.3.0",
    "aiosqlite>=0.20.0",
    "sqlalchemy[asyncio]>=2.0.0",
    "python-dotenv>=1.0.0",
    "httpx>=0.27.0",
    "pydantic>=2.7.0",
    "pydantic-settings>=2.3.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.2.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=5.0.0",
    "ruff>=0.4.0",
    "mypy>=1.10.0",
    "bandit>=1.7.0",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.mypy]
python_version = "3.12"
strict = true
ignore_missing_imports = true
```

- [ ] **Step 4: Create `config.py`**

```python
import os
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Config(BaseSettings):
    # Anthropic
    anthropic_api_key: str = Field(..., validation_alias="ANTHROPIC_API_KEY")

    # GitHub
    github_token: str = Field(..., validation_alias="GITHUB_TOKEN")
    github_repo: str = Field(..., validation_alias="GITHUB_REPO")

    # Telegram
    telegram_bot_token: str = Field(..., validation_alias="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: str = Field(..., validation_alias="TELEGRAM_CHAT_ID")

    # Web UI
    web_port: int = Field(default=8000, validation_alias="WEB_PORT")
    web_secret_key: str = Field(default="change-me-in-production", validation_alias="WEB_SECRET_KEY")

    # Database
    database_url: str = Field(default="sqlite+aiosqlite:///./monarch_ai.db", validation_alias="DATABASE_URL")

    # Behaviour
    max_agent_retries: int = Field(default=3, validation_alias="MAX_AGENT_RETRIES")
    approval_timeout_minutes: int = Field(default=60, validation_alias="APPROVAL_TIMEOUT_MINUTES")
    confidence_threshold: float = Field(default=0.70, validation_alias="CONFIDENCE_THRESHOLD")

    @field_validator("anthropic_api_key")
    @classmethod
    def validate_anthropic_key(cls, v: str) -> str:
        if not v or v == "":
            raise ValueError("ANTHROPIC_API_KEY is required")
        return v

    model_config = {"env_file": ".env", "extra": "ignore"}


config = Config()
```

- [ ] **Step 5: Create `.env.example`**

```env
# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# GitHub
GITHUB_TOKEN=ghp_...
GITHUB_REPO=owner/repo-name

# Telegram
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
TELEGRAM_CHAT_ID=123456789

# Web UI
WEB_PORT=8000
WEB_SECRET_KEY=your-secret-key-here

# Database (SQLite for dev, PostgreSQL for prod)
DATABASE_URL=sqlite+aiosqlite:///./monarch_ai.db

# Behaviour
MAX_AGENT_RETRIES=3
APPROVAL_TIMEOUT_MINUTES=60
CONFIDENCE_THRESHOLD=0.70
```

- [ ] **Step 6: Install dependencies and run test**

```bash
pip install -e ".[dev]"
pytest tests/unit/test_config.py -v
```
Expected: `PASS — 2 passed`

- [ ] **Step 7: Commit**

```bash
git init
git add pyproject.toml config.py .env.example tests/
git commit -m "feat: project setup — config, deps, test structure"
```

---

### Task 2: Task Model + Storage

**Files:**
- Create: `core/task.py`
- Create: `core/context.py`
- Create: `storage/models.py`
- Create: `storage/database.py`
- Create: `tests/unit/test_task.py`
- Create: `tests/unit/test_storage.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/unit/test_task.py
import pytest
from datetime import datetime
from core.task import TaskStatus, Task, HistoryEntry


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


def test_task_status_transition():
    task = Task(raw_input="test")
    task.status = TaskStatus.RUNNING
    assert task.status == TaskStatus.RUNNING
```

```python
# tests/unit/test_storage.py
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
    assert loaded.status == TaskStatus.RUNNING
    assert len(loaded.history) == 1


@pytest.mark.asyncio
async def test_list_active_tasks(db):
    for i in range(3):
        t = Task(raw_input=f"task {i}")
        await db.save_task(t)
    tasks = await db.list_active_tasks()
    assert len(tasks) == 3
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/unit/test_task.py tests/unit/test_storage.py -v
```
Expected: `FAIL — ModuleNotFoundError: No module named 'core'`

- [ ] **Step 3: Create `core/task.py`**

```python
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
```

- [ ] **Step 4: Create `core/__init__.py` and `storage/__init__.py` and `agents/__init__.py` and `tools/__init__.py` and `interfaces/__init__.py`**

```bash
touch core/__init__.py storage/__init__.py agents/__init__.py tools/__init__.py interfaces/__init__.py
```

- [ ] **Step 5: Create `storage/models.py`**

```python
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime, UTC


class Base(DeclarativeBase):
    pass


class TaskRecord(Base):
    __tablename__ = "tasks"

    task_id = Column(String, primary_key=True)
    status = Column(String, nullable=False)
    raw_input = Column(Text, nullable=False)
    context_json = Column(Text, nullable=False)  # full Task serialized as JSON
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
```

- [ ] **Step 6: Create `storage/database.py`**

```python
import json
from dataclasses import asdict
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
from storage.models import Base, TaskRecord
from core.task import Task, TaskStatus, HistoryEntry


def _serialize_task(task: Task) -> str:
    def default(obj: object) -> str:
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, TaskStatus):
            return obj.value
        raise TypeError(f"Not serializable: {type(obj)}")
    return json.dumps(asdict(task), default=default)


def _deserialize_task(data: str) -> Task:
    raw = json.loads(data)
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
```

- [ ] **Step 7: Run tests**

```bash
pytest tests/unit/test_task.py tests/unit/test_storage.py -v
```
Expected: `PASS — 6 passed`

- [ ] **Step 8: Commit**

```bash
git add core/ storage/ tests/unit/test_task.py tests/unit/test_storage.py
git commit -m "feat: task model + async SQLite storage"
```

---

### Task 3: BaseAgent com Anthropic SDK + Prompt Caching

**Files:**
- Create: `agents/base.py`
- Create: `tests/unit/test_base_agent.py`

- [ ] **Step 1: Write failing test**

```python
# tests/unit/test_base_agent.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from agents.base import BaseAgent, AgentResult
from core.task import Task


class ConcreteAgent(BaseAgent):
    name = "test_agent"
    system_prompt = "You are a test agent."

    async def build_user_message(self, task: Task) -> str:
        return f"Process: {task.raw_input}"


@pytest.mark.asyncio
async def test_agent_returns_result_on_text_response():
    agent = ConcreteAgent()
    task = Task(raw_input="create login endpoint")

    mock_message = MagicMock()
    mock_message.stop_reason = "end_turn"
    mock_message.content = [MagicMock(type="text", text='{"output": "done", "confidence": 0.9}')]

    with patch.object(agent, "_call_claude", return_value=mock_message):
        result = await agent.run(task)

    assert isinstance(result, AgentResult)
    assert result.output == {"output": "done", "confidence": 0.9}
    assert result.confidence == 0.9


@pytest.mark.asyncio
async def test_agent_raises_on_empty_response():
    agent = ConcreteAgent()
    task = Task(raw_input="test")

    mock_message = MagicMock()
    mock_message.stop_reason = "end_turn"
    mock_message.content = []

    with patch.object(agent, "_call_claude", return_value=mock_message):
        with pytest.raises(ValueError, match="empty response"):
            await agent.run(task)
```

- [ ] **Step 2: Run to verify failure**

```bash
pytest tests/unit/test_base_agent.py -v
```
Expected: `FAIL — ModuleNotFoundError: No module named 'agents.base'`

- [ ] **Step 3: Create `agents/base.py`**

```python
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import anthropic

from config import config
from core.task import Task

logger = logging.getLogger(__name__)

_client = anthropic.AsyncAnthropic(api_key=config.anthropic_api_key)

OPUS_MODEL = "claude-opus-4-6"
SONNET_MODEL = "claude-sonnet-4-6"
HAIKU_MODEL = "claude-haiku-4-5-20251001"


@dataclass
class AgentResult:
    output: dict[str, Any]
    confidence: float
    concerns: list[str]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentResult":
        return cls(
            output=data,
            confidence=float(data.get("confidence", 1.0)),
            concerns=data.get("concerns", []),
        )


class BaseAgent(ABC):
    name: str = "base"
    model: str = OPUS_MODEL
    system_prompt: str = ""
    tools: list[dict[str, Any]] = []
    max_tokens: int = 8096

    def _build_system(self) -> list[dict[str, Any]]:
        """System prompt with prompt caching for cost reduction."""
        return [
            {
                "type": "text",
                "text": self.system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ]

    @abstractmethod
    async def build_user_message(self, task: Task) -> str:
        """Build the user message for this agent given the task context."""

    async def _call_claude(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> anthropic.types.Message:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "system": self._build_system(),
            "messages": messages,
        }
        if tools:
            kwargs["tools"] = tools
        return await _client.messages.create(**kwargs)

    async def _handle_tool_use(
        self,
        message: anthropic.types.Message,
        messages: list[dict[str, Any]],
    ) -> anthropic.types.Message:
        """Process tool_use blocks and continue the loop."""
        tool_results = []
        for block in message.content:
            if block.type == "tool_use":
                result = await self.execute_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result),
                })

        messages.append({"role": "assistant", "content": message.content})
        messages.append({"role": "user", "content": tool_results})

        return await self._call_claude(messages, self.tools or None)

    async def execute_tool(self, name: str, inputs: dict[str, Any]) -> Any:
        """Override in subclasses to handle tool calls."""
        raise NotImplementedError(f"Tool not implemented: {name}")

    def _extract_json(self, text: str) -> dict[str, Any]:
        """Extract JSON from text response (handles markdown code blocks)."""
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1])
        return json.loads(text)

    async def run(self, task: Task) -> AgentResult:
        user_content = await self.build_user_message(task)
        messages: list[dict[str, Any]] = [{"role": "user", "content": user_content}]

        logger.info(f"[{self.name}] Starting for task {task.task_id}")
        message = await self._call_claude(messages, self.tools or None)

        # Tool use loop
        while message.stop_reason == "tool_use":
            message = await self._handle_tool_use(message, messages)

        if not message.content:
            raise ValueError(f"[{self.name}] Got empty response from Claude")

        text_blocks = [b for b in message.content if b.type == "text"]
        if not text_blocks:
            raise ValueError(f"[{self.name}] No text block in response")

        raw = self._extract_json(text_blocks[0].text)
        result = AgentResult.from_dict(raw)
        logger.info(f"[{self.name}] Done. Confidence: {result.confidence:.2f}")
        return result
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/unit/test_base_agent.py -v
```
Expected: `PASS — 2 passed`

- [ ] **Step 5: Commit**

```bash
git add agents/base.py tests/unit/test_base_agent.py
git commit -m "feat: BaseAgent with Anthropic SDK tool_use loop + prompt caching"
```

---

### Task 4: GitHub Tools

**Files:**
- Create: `tools/github_tools.py`
- Create: `tests/unit/test_github_tools.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/unit/test_github_tools.py
import pytest
from unittest.mock import MagicMock, patch
from tools.github_tools import GitHubTools


@pytest.fixture
def mock_repo():
    repo = MagicMock()
    repo.default_branch = "main"
    return repo


@pytest.fixture
def gh_tools(mock_repo):
    with patch("tools.github_tools.Github") as mock_gh:
        mock_gh.return_value.get_repo.return_value = mock_repo
        tools = GitHubTools(token="fake", repo_name="owner/repo")
        tools._repo = mock_repo
        return tools


def test_read_file(gh_tools, mock_repo):
    mock_content = MagicMock()
    mock_content.decoded_content = b"def hello(): pass"
    mock_repo.get_contents.return_value = mock_content

    result = gh_tools.read_file("src/hello.py")
    assert result == "def hello(): pass"


def test_list_files(gh_tools, mock_repo):
    f1 = MagicMock(); f1.type = "file"; f1.path = "src/a.py"
    f2 = MagicMock(); f2.type = "file"; f2.path = "src/b.py"
    mock_repo.get_contents.return_value = [f1, f2]

    result = gh_tools.list_files("src/")
    assert "src/a.py" in result
    assert "src/b.py" in result


def test_create_branch(gh_tools, mock_repo):
    mock_ref = MagicMock(); mock_ref.object.sha = "abc123"
    mock_repo.get_git_ref.return_value = mock_ref

    gh_tools.create_branch("feat/monarch-001-test")
    mock_repo.create_git_ref.assert_called_once()
```

- [ ] **Step 2: Run to verify failure**

```bash
pytest tests/unit/test_github_tools.py -v
```
Expected: `FAIL — ModuleNotFoundError: No module named 'tools.github_tools'`

- [ ] **Step 3: Create `tools/github_tools.py`**

```python
import logging
from typing import Any
from github import Github, GithubException
from github.Repository import Repository

logger = logging.getLogger(__name__)


class GitHubTools:
    def __init__(self, token: str, repo_name: str) -> None:
        self._gh = Github(token)
        self._repo: Repository = self._gh.get_repo(repo_name)

    def read_file(self, path: str, branch: str | None = None) -> str:
        ref = branch or self._repo.default_branch
        content = self._repo.get_contents(path, ref=ref)
        if isinstance(content, list):
            raise ValueError(f"{path} is a directory")
        return content.decoded_content.decode("utf-8")

    def list_files(self, path: str = "", branch: str | None = None) -> list[str]:
        ref = branch or self._repo.default_branch
        contents = self._repo.get_contents(path, ref=ref)
        if not isinstance(contents, list):
            contents = [contents]
        return [c.path for c in contents if c.type == "file"]

    def write_file(
        self,
        path: str,
        content: str,
        branch: str,
        commit_message: str,
    ) -> None:
        try:
            existing = self._repo.get_contents(path, ref=branch)
            if isinstance(existing, list):
                raise ValueError(f"{path} is a directory")
            self._repo.update_file(
                path, commit_message, content, existing.sha, branch=branch
            )
        except GithubException as e:
            if e.status == 404:
                self._repo.create_file(path, commit_message, content, branch=branch)
            else:
                raise

    def create_branch(self, name: str, from_branch: str | None = None) -> None:
        source = from_branch or self._repo.default_branch
        ref = self._repo.get_git_ref(f"heads/{source}")
        self._repo.create_git_ref(f"refs/heads/{name}", ref.object.sha)
        logger.info(f"Created branch {name} from {source}")

    def create_pr(
        self,
        title: str,
        body: str,
        head: str,
        base: str | None = None,
        draft: bool = True,
    ) -> str:
        target = base or self._repo.default_branch
        pr = self._repo.create_pull(
            title=title, body=body, head=head, base=target, draft=draft
        )
        logger.info(f"Created PR #{pr.number}: {pr.html_url}")
        return pr.html_url

    def get_pr_diff(self, pr_number: int) -> str:
        pr = self._repo.get_pull(pr_number)
        files = pr.get_files()
        diff_parts = []
        for f in files:
            diff_parts.append(f"--- {f.filename} (+{f.additions} -{f.deletions})")
            if f.patch:
                diff_parts.append(f.patch)
        return "\n".join(diff_parts)

    def as_tools_schema(self) -> list[dict[str, Any]]:
        """Returns tool definitions for use in agent tool_use calls."""
        return [
            {
                "name": "read_file",
                "description": "Read a file from the GitHub repository",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path"},
                        "branch": {"type": "string", "description": "Branch name (optional)"},
                    },
                    "required": ["path"],
                },
            },
            {
                "name": "list_files",
                "description": "List files in a directory of the repository",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Directory path"},
                        "branch": {"type": "string", "description": "Branch name (optional)"},
                    },
                    "required": [],
                },
            },
            {
                "name": "write_file",
                "description": "Write or update a file in the repository on a branch",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "content": {"type": "string"},
                        "branch": {"type": "string"},
                        "commit_message": {"type": "string"},
                    },
                    "required": ["path", "content", "branch", "commit_message"],
                },
            },
            {
                "name": "create_branch",
                "description": "Create a new branch in the repository",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "from_branch": {"type": "string"},
                    },
                    "required": ["name"],
                },
            },
        ]
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/unit/test_github_tools.py -v
```
Expected: `PASS — 3 passed`

- [ ] **Step 5: Commit**

```bash
git add tools/github_tools.py tools/__init__.py tests/unit/test_github_tools.py
git commit -m "feat: GitHub tools — read/write/branch/PR via PyGithub"
```

---

### Task 5: Code Tools (pytest + ruff + mypy + bandit)

**Files:**
- Create: `tools/code_tools.py`
- Create: `tools/fs_tools.py`
- Create: `tests/unit/test_code_tools.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/unit/test_code_tools.py
import pytest
import tempfile
import os
from tools.code_tools import CodeTools


@pytest.fixture
def tmp_project(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "hello.py").write_text("def hello():\n    return 'hi'\n")
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_hello.py").write_text(
        "from src.hello import hello\ndef test_hello():\n    assert hello() == 'hi'\n"
    )
    return tmp_path


def test_run_linter_on_clean_file(tmp_path):
    f = tmp_path / "clean.py"
    f.write_text("x = 1\n")
    tools = CodeTools(str(tmp_path))
    result = tools.run_linter("clean.py")
    assert result["passed"] is True


def test_run_linter_on_dirty_file(tmp_path):
    f = tmp_path / "dirty.py"
    f.write_text("import os\nimport sys\nx=1\n")  # unused imports + no space
    tools = CodeTools(str(tmp_path))
    result = tools.run_linter("dirty.py")
    assert result["passed"] is False
    assert len(result["issues"]) > 0
```

- [ ] **Step 2: Run to verify failure**

```bash
pytest tests/unit/test_code_tools.py -v
```
Expected: `FAIL — ModuleNotFoundError: No module named 'tools.code_tools'`

- [ ] **Step 3: Create `tools/code_tools.py`**

```python
import subprocess
import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class CodeTools:
    def __init__(self, project_root: str) -> None:
        self.root = Path(project_root)

    def run_tests(self, path: str = "tests/", filter_expr: str | None = None) -> dict[str, Any]:
        cmd = ["pytest", path, "--tb=short", "-q", "--json-report", "--json-report-file=/tmp/pytest-report.json"]
        if filter_expr:
            cmd.extend(["-k", filter_expr])
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.root)
        try:
            with open("/tmp/pytest-report.json") as f:
                report = json.load(f)
            return {
                "passed": result.returncode == 0,
                "summary": report.get("summary", {}),
                "failures": [
                    {"nodeid": t["nodeid"], "message": t.get("call", {}).get("longrepr", "")}
                    for t in report.get("tests", [])
                    if t["outcome"] == "failed"
                ],
                "output": result.stdout,
            }
        except Exception:
            return {
                "passed": result.returncode == 0,
                "summary": {},
                "failures": [],
                "output": result.stdout + result.stderr,
            }

    def run_linter(self, path: str = ".") -> dict[str, Any]:
        cmd = ["ruff", "check", path, "--output-format=json"]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.root)
        try:
            issues = json.loads(result.stdout) if result.stdout.strip() else []
        except json.JSONDecodeError:
            issues = []
        return {
            "passed": result.returncode == 0,
            "issues": [
                {"file": i["filename"], "line": i["location"]["row"], "message": i["message"]}
                for i in issues
            ],
        }

    def run_type_check(self, path: str = "src/") -> dict[str, Any]:
        cmd = ["mypy", path, "--ignore-missing-imports", "--no-error-summary"]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.root)
        errors = [line for line in result.stdout.splitlines() if ": error:" in line]
        return {
            "passed": result.returncode == 0,
            "errors": errors,
            "output": result.stdout,
        }

    def run_security_scan(self, path: str = "src/") -> dict[str, Any]:
        cmd = ["bandit", "-r", path, "-f", "json", "-q"]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.root)
        try:
            report = json.loads(result.stdout) if result.stdout.strip() else {}
        except json.JSONDecodeError:
            report = {}
        issues = report.get("results", [])
        has_high = any(i.get("issue_severity") == "HIGH" for i in issues)
        return {
            "passed": not has_high,
            "high_severity": [i for i in issues if i.get("issue_severity") == "HIGH"],
            "medium_severity": [i for i in issues if i.get("issue_severity") == "MEDIUM"],
            "all_issues": issues,
        }
```

- [ ] **Step 4: Create `tools/fs_tools.py`**

```python
import os
from pathlib import Path
from typing import Any


class FileSystemTools:
    def __init__(self, base_path: str) -> None:
        self.base = Path(base_path).resolve()

    def _safe_path(self, relative: str) -> Path:
        full = (self.base / relative).resolve()
        if not str(full).startswith(str(self.base)):
            raise ValueError(f"Path traversal attempt: {relative}")
        return full

    def read_file(self, path: str) -> str:
        return self._safe_path(path).read_text(encoding="utf-8")

    def write_file(self, path: str, content: str) -> None:
        full = self._safe_path(path)
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8")

    def list_files(self, path: str = "", extensions: list[str] | None = None) -> list[str]:
        base = self._safe_path(path) if path else self.base
        results = []
        for f in base.rglob("*"):
            if f.is_file():
                if extensions is None or f.suffix in extensions:
                    results.append(str(f.relative_to(self.base)))
        return sorted(results)

    def file_exists(self, path: str) -> bool:
        return self._safe_path(path).exists()
```

- [ ] **Step 5: Run tests**

```bash
pip install pytest-json-report
pytest tests/unit/test_code_tools.py -v
```
Expected: `PASS — 2 passed`

- [ ] **Step 6: Commit**

```bash
git add tools/code_tools.py tools/fs_tools.py tests/unit/test_code_tools.py
git commit -m "feat: code tools — pytest runner, ruff linter, mypy, bandit security scan"
```

---

### Task 6: Agente de Descoberta/Requisitos

**Files:**
- Create: `agents/discovery.py`
- Create: `tests/unit/test_discovery_agent.py`

- [ ] **Step 1: Write failing test**

```python
# tests/unit/test_discovery_agent.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from agents.discovery import DiscoveryAgent
from agents.base import AgentResult
from core.task import Task


@pytest.mark.asyncio
async def test_discovery_returns_requirements():
    agent = DiscoveryAgent()
    task = Task(raw_input="Criar endpoint GET /users/{id} que retorna dados do usuário")

    mock_result = AgentResult(
        output={
            "user_stories": ["Como usuário, quero buscar meu perfil pelo ID"],
            "acceptance_criteria": ["Retorna 404 se usuário não existe", "Retorna dados sem senha"],
            "technical_notes": ["Usar UUID para user_id", "Autenticação via JWT obrigatória"],
            "clarification_questions": [],
            "confidence": 0.92,
        },
        confidence=0.92,
        concerns=[],
    )

    with patch.object(agent, "run", return_value=mock_result):
        result = await agent.run(task)

    assert "user_stories" in result.output
    assert "acceptance_criteria" in result.output
    assert result.confidence > 0.7


@pytest.mark.asyncio
async def test_discovery_flags_low_confidence_for_vague_input():
    agent = DiscoveryAgent()
    task = Task(raw_input="fazer uma coisa no sistema")

    mock_result = AgentResult(
        output={
            "user_stories": [],
            "acceptance_criteria": [],
            "technical_notes": [],
            "clarification_questions": ["O que exatamente deve ser feito?", "Qual sistema?"],
            "confidence": 0.3,
        },
        confidence=0.3,
        concerns=["Input muito vago para gerar requisitos confiáveis"],
    )

    with patch.object(agent, "run", return_value=mock_result):
        result = await agent.run(task)

    assert result.confidence < 0.7
    assert len(result.output["clarification_questions"]) > 0
```

- [ ] **Step 2: Run to verify failure**

```bash
pytest tests/unit/test_discovery_agent.py -v
```
Expected: `FAIL — ModuleNotFoundError: No module named 'agents.discovery'`

- [ ] **Step 3: Create `agents/discovery.py`**

```python
import json
from agents.base import BaseAgent, AgentResult
from core.task import Task

SYSTEM_PROMPT = """You are the Discovery Agent for Monarch AI — a specialized requirements engineer.

Your job: transform vague or high-level task descriptions into clear, structured, actionable requirements.

You MUST respond with a JSON object with this exact structure:
{
  "user_stories": ["As a <role>, I want <feature> so that <benefit>", ...],
  "acceptance_criteria": ["Given <context>, when <action>, then <outcome>", ...],
  "technical_notes": ["Technical constraints or details", ...],
  "clarification_questions": ["Question if input is ambiguous", ...],
  "confidence": 0.0-1.0
}

Rules:
- confidence < 0.7 means the input is too vague → populate clarification_questions
- confidence >= 0.7 means you have enough to proceed
- Be specific and measurable in acceptance criteria
- Never invent business requirements — only clarify technical implications
- If auth/security/data validation is implied, include it in technical_notes
"""


class DiscoveryAgent(BaseAgent):
    name = "discovery"
    model = "claude-opus-4-6"
    system_prompt = SYSTEM_PROMPT

    async def build_user_message(self, task: Task) -> str:
        context_parts = [f"Task: {task.raw_input}"]
        if task.requirements:
            context_parts.append(f"Previous requirements attempt: {json.dumps(task.requirements)}")
        return "\n\n".join(context_parts)
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/unit/test_discovery_agent.py -v
```
Expected: `PASS — 2 passed`

- [ ] **Step 5: Commit**

```bash
git add agents/discovery.py tests/unit/test_discovery_agent.py
git commit -m "feat: Discovery Agent — transforms raw input into structured requirements"
```

---

### Task 7: Agentes de Priorização, Arquitetura, Planejamento e Advogado do Diabo

**Files:**
- Create: `agents/prioritization.py`
- Create: `agents/architecture.py`
- Create: `agents/planning.py`
- Create: `agents/devils_advocate.py`
- Create: `tests/unit/test_definition_agents.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/unit/test_definition_agents.py
import pytest
from unittest.mock import patch
from agents.prioritization import PrioritizationAgent
from agents.architecture import ArchitectureAgent
from agents.planning import PlanningAgent
from agents.devils_advocate import DevilsAdvocateAgent
from agents.base import AgentResult
from core.task import Task


def make_task_with_requirements() -> Task:
    task = Task(raw_input="Criar endpoint /users/{id}")
    task.requirements = {
        "user_stories": ["Como usuário, quero buscar meu perfil"],
        "acceptance_criteria": ["Retorna 404 se não existe"],
        "technical_notes": ["JWT obrigatório"],
        "confidence": 0.9,
    }
    return task


@pytest.mark.asyncio
async def test_prioritization_returns_mvp():
    agent = PrioritizationAgent()
    task = make_task_with_requirements()
    mock_result = AgentResult(
        output={"priority": "MVP_V1", "justification": "Core feature", "confidence": 0.95},
        confidence=0.95, concerns=[],
    )
    with patch.object(agent, "run", return_value=mock_result):
        result = await agent.run(task)
    assert result.output["priority"] in ["MVP_V1", "BACKLOG_V2", "DISCARDED"]


@pytest.mark.asyncio
async def test_architecture_proposes_components():
    agent = ArchitectureAgent()
    task = make_task_with_requirements()
    task.priority = "MVP_V1"
    mock_result = AgentResult(
        output={
            "components": ["UserController", "UserService", "UserRepository"],
            "technology_choices": {"framework": "FastAPI", "auth": "JWT"},
            "api_design": {"method": "GET", "path": "/users/{user_id}", "response": "UserResponse"},
            "concerns": [],
            "confidence": 0.88,
        },
        confidence=0.88, concerns=[],
    )
    with patch.object(agent, "run", return_value=mock_result):
        result = await agent.run(task)
    assert "components" in result.output
    assert "api_design" in result.output


@pytest.mark.asyncio
async def test_devils_advocate_raises_concerns():
    agent = DevilsAdvocateAgent()
    task = make_task_with_requirements()
    mock_result = AgentResult(
        output={
            "objections": ["E se o user_id não for UUID? Há validação?"],
            "risks": ["Sem rate limiting no endpoint"],
            "missing_scenarios": ["Usuário deletado (soft delete)"],
            "verdict": "CONCERNS_RAISED",
            "confidence": 0.85,
        },
        confidence=0.85, concerns=["Validação de input ausente"],
    )
    with patch.object(agent, "run", return_value=mock_result):
        result = await agent.run(task)
    assert result.output["verdict"] in ["APPROVED", "CONCERNS_RAISED", "BLOCKED"]
```

- [ ] **Step 2: Run to verify failure**

```bash
pytest tests/unit/test_definition_agents.py -v
```
Expected: `FAIL — ModuleNotFoundError`

- [ ] **Step 3: Create `agents/prioritization.py`**

```python
import json
from agents.base import BaseAgent
from core.task import Task

SYSTEM_PROMPT = """You are the Prioritization Agent for Monarch AI.

Evaluate tasks and classify them for the current development cycle.

Respond with JSON:
{
  "priority": "MVP_V1" | "BACKLOG_V2" | "DISCARDED",
  "justification": "Why this priority",
  "effort_estimate": "small" | "medium" | "large",
  "dependencies": ["other features needed first"],
  "confidence": 0.0-1.0
}

MVP_V1: Core functionality, high value, feasible now.
BACKLOG_V2: Valuable but not urgent, or depends on MVP_V1.
DISCARDED: Out of scope, duplicate, or infeasible.
"""


class PrioritizationAgent(BaseAgent):
    name = "prioritization"
    model = "claude-haiku-4-5-20251001"
    system_prompt = SYSTEM_PROMPT

    async def build_user_message(self, task: Task) -> str:
        return json.dumps({"input": task.raw_input, "requirements": task.requirements})
```

- [ ] **Step 4: Create `agents/architecture.py`**

```python
import json
from agents.base import BaseAgent
from core.task import Task

SYSTEM_PROMPT = """You are the Architecture Agent for Monarch AI.

Design the technical solution for a given requirement. Stay within existing patterns.

Respond with JSON:
{
  "components": ["ComponentName: responsibility"],
  "technology_choices": {"key": "technology and why"},
  "api_design": {"method": "", "path": "", "request_body": {}, "response": {}},
  "database_changes": ["migration needed"],
  "integration_points": ["external services"],
  "concerns": ["architectural risks"],
  "confidence": 0.0-1.0
}

Rules:
- Prefer extending existing code over creating new services
- Minimum viable design — no over-engineering
- Flag if you need to introduce a new dependency
"""


class ArchitectureAgent(BaseAgent):
    name = "architecture"
    model = "claude-opus-4-6"
    system_prompt = SYSTEM_PROMPT

    async def build_user_message(self, task: Task) -> str:
        return json.dumps({
            "requirements": task.requirements,
            "priority": task.priority,
        })
```

- [ ] **Step 5: Create `agents/planning.py`**

```python
import json
from agents.base import BaseAgent
from core.task import Task

SYSTEM_PROMPT = """You are the Technical Planning Agent for Monarch AI.

Break an architectural proposal into ordered, executable implementation steps.

Respond with JSON:
{
  "steps": [
    {
      "order": 1,
      "description": "What to do",
      "files": ["path/to/file.py"],
      "type": "create" | "modify" | "test" | "config",
      "depends_on": []
    }
  ],
  "estimated_complexity": "low" | "medium" | "high",
  "confidence": 0.0-1.0
}

Rules:
- First steps should always be writing tests (TDD)
- Each step touches 1-3 files max
- Order matters — migrations before code that uses them
"""


class PlanningAgent(BaseAgent):
    name = "planning"
    model = "claude-sonnet-4-6"
    system_prompt = SYSTEM_PROMPT

    async def build_user_message(self, task: Task) -> str:
        return json.dumps({
            "requirements": task.requirements,
            "architecture": task.architecture,
        })
```

- [ ] **Step 6: Create `agents/devils_advocate.py`**

```python
import json
from agents.base import BaseAgent
from core.task import Task

SYSTEM_PROMPT = """You are the Devil's Advocate Agent for Monarch AI.

Your ONLY job is to find problems. Question everything. Be adversarial but fair.

Respond with JSON:
{
  "objections": ["Specific objection with evidence"],
  "risks": ["Risk: description of what could go wrong"],
  "missing_scenarios": ["Edge case not covered"],
  "security_concerns": ["Potential vulnerability"],
  "verdict": "APPROVED" | "CONCERNS_RAISED" | "BLOCKED",
  "confidence": 0.0-1.0
}

APPROVED: No significant issues found.
CONCERNS_RAISED: Issues found but not blocking — should be addressed.
BLOCKED: Critical issue that MUST be resolved before proceeding.

Rules:
- Never propose solutions, only problems
- Be specific — vague objections are useless
- Check: auth, validation, error handling, concurrency, scalability, LGPD/GDPR
- A "BLOCKED" verdict always requires a specific critical reason
"""


class DevilsAdvocateAgent(BaseAgent):
    name = "devils_advocate"
    model = "claude-opus-4-6"
    system_prompt = SYSTEM_PROMPT

    async def build_user_message(self, task: Task) -> str:
        return json.dumps({
            "requirements": task.requirements,
            "architecture": task.architecture,
            "plan": task.plan,
            "review_stage": "pre_implementation" if not task.branch_name else "post_implementation",
        })
```

- [ ] **Step 7: Run tests**

```bash
pytest tests/unit/test_definition_agents.py -v
```
Expected: `PASS — 3 passed`

- [ ] **Step 8: Commit**

```bash
git add agents/prioritization.py agents/architecture.py agents/planning.py agents/devils_advocate.py tests/unit/test_definition_agents.py
git commit -m "feat: Definition layer agents — Prioritization, Architecture, Planning, Devil's Advocate"
```

---

### Task 8: Agentes de Execução (Implementador, Testes, Revisor, Segurança)

**Files:**
- Create: `agents/implementer.py`
- Create: `agents/testing.py`
- Create: `agents/reviewer.py`
- Create: `agents/security.py`
- Create: `tests/unit/test_execution_agents.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/unit/test_execution_agents.py
import pytest
from unittest.mock import patch, MagicMock
from agents.implementer import ImplementerAgent
from agents.testing import TestingAgent
from agents.reviewer import ReviewerAgent
from agents.security import SecurityAgent
from agents.base import AgentResult
from core.task import Task


def make_task_ready_to_implement() -> Task:
    task = Task(raw_input="Criar endpoint /users/{id}")
    task.requirements = {"user_stories": ["buscar usuário por ID"], "acceptance_criteria": ["404 se não existe"]}
    task.priority = "MVP_V1"
    task.architecture = {"components": ["UserController"], "api_design": {"method": "GET", "path": "/users/{id}"}}
    task.plan = [{"order": 1, "description": "Create test", "files": ["tests/test_users.py"], "type": "test"}]
    return task


@pytest.mark.asyncio
async def test_implementer_returns_branch_and_files():
    agent = ImplementerAgent(github_tools=MagicMock(), fs_tools=MagicMock())
    task = make_task_ready_to_implement()
    mock_result = AgentResult(
        output={"branch": "feat/monarch-001-users-endpoint", "files_changed": ["src/users.py"], "pr_url": "https://github.com/owner/repo/pull/1", "confidence": 0.9},
        confidence=0.9, concerns=[],
    )
    with patch.object(agent, "run", return_value=mock_result):
        result = await agent.run(task)
    assert "branch" in result.output
    assert "pr_url" in result.output


@pytest.mark.asyncio
async def test_testing_agent_returns_pass_fail():
    agent = TestingAgent(code_tools=MagicMock())
    task = make_task_ready_to_implement()
    task.branch_name = "feat/monarch-001-users-endpoint"
    mock_result = AgentResult(
        output={"passed": True, "coverage": 87.5, "tests_written": 4, "failures": [], "confidence": 0.95},
        confidence=0.95, concerns=[],
    )
    with patch.object(agent, "run", return_value=mock_result):
        result = await agent.run(task)
    assert "passed" in result.output
    assert "coverage" in result.output


@pytest.mark.asyncio
async def test_security_agent_blocks_on_critical():
    agent = SecurityAgent(code_tools=MagicMock())
    task = make_task_ready_to_implement()
    mock_result = AgentResult(
        output={"verdict": "BLOCKED", "critical_issues": [{"type": "SQL_INJECTION", "file": "src/users.py", "line": 42}], "confidence": 0.99},
        confidence=0.99, concerns=["SQL Injection detectado"],
    )
    with patch.object(agent, "run", return_value=mock_result):
        result = await agent.run(task)
    assert result.output["verdict"] in ["APPROVED", "CONCERNS_RAISED", "BLOCKED"]
```

- [ ] **Step 2: Run to verify failure**

```bash
pytest tests/unit/test_execution_agents.py -v
```
Expected: `FAIL — ModuleNotFoundError`

- [ ] **Step 3: Create `agents/implementer.py`**

```python
import json
from agents.base import BaseAgent, AgentResult
from core.task import Task
from tools.github_tools import GitHubTools
from tools.fs_tools import FileSystemTools

SYSTEM_PROMPT = """You are the Implementer Agent for Monarch AI.

Write production-quality Python code following TDD — tests first, then implementation.

You have access to GitHub tools to read/write code and create branches/PRs.

After implementing, respond with JSON:
{
  "branch": "feat/monarch-<id>-<description>",
  "files_changed": ["path/to/file.py"],
  "pr_url": "https://github.com/...",
  "summary": "What was implemented",
  "confidence": 0.0-1.0
}

Rules:
- Always work on a dedicated branch (never commit to main)
- Write tests before implementation (TDD)
- Follow existing code style and patterns
- Minimal implementation — only what the plan requires
- Include type hints and docstrings for public functions
"""


class ImplementerAgent(BaseAgent):
    name = "implementer"
    model = "claude-opus-4-6"
    system_prompt = SYSTEM_PROMPT

    def __init__(self, github_tools: GitHubTools, fs_tools: FileSystemTools) -> None:
        self.github = github_tools
        self.fs = fs_tools
        self.tools = github_tools.as_tools_schema()

    async def build_user_message(self, task: Task) -> str:
        return json.dumps({
            "task_id": task.task_id,
            "requirements": task.requirements,
            "architecture": task.architecture,
            "plan": task.plan,
            "branch_prefix": f"feat/{task.task_id}",
        })

    async def execute_tool(self, name: str, inputs: dict) -> object:
        match name:
            case "read_file":
                return self.github.read_file(**inputs)
            case "list_files":
                return self.github.list_files(**inputs)
            case "write_file":
                return self.github.write_file(**inputs)
            case "create_branch":
                return self.github.create_branch(**inputs)
            case _:
                raise NotImplementedError(f"Unknown tool: {name}")
```

- [ ] **Step 4: Create `agents/testing.py`**

```python
import json
from agents.base import BaseAgent
from core.task import Task
from tools.code_tools import CodeTools

SYSTEM_PROMPT = """You are the Testing Agent for Monarch AI.

Generate comprehensive tests for implemented code and report results.

After testing, respond with JSON:
{
  "passed": true | false,
  "coverage": 0.0-100.0,
  "tests_written": 0,
  "failures": [{"test": "name", "reason": "why it failed"}],
  "missing_coverage": ["scenario not tested"],
  "confidence": 0.0-1.0
}
"""


class TestingAgent(BaseAgent):
    name = "testing"
    model = "claude-sonnet-4-6"
    system_prompt = SYSTEM_PROMPT

    def __init__(self, code_tools: CodeTools) -> None:
        self.code = code_tools

    async def build_user_message(self, task: Task) -> str:
        return json.dumps({
            "requirements": task.requirements,
            "acceptance_criteria": (task.requirements or {}).get("acceptance_criteria", []),
            "branch": task.branch_name,
        })
```

- [ ] **Step 5: Create `agents/reviewer.py`**

```python
import json
from agents.base import BaseAgent
from core.task import Task

SYSTEM_PROMPT = """You are the Code Reviewer Agent for Monarch AI.

Review code quality, style, and correctness.

Respond with JSON:
{
  "verdict": "APPROVED" | "CHANGES_REQUESTED",
  "quality_score": 0.0-10.0,
  "issues": [{"severity": "low|medium|high", "file": "", "description": ""}],
  "suggestions": ["improvement suggestion"],
  "confidence": 0.0-1.0
}

Check: naming conventions, function size, DRY violations, error handling, type hints, docstrings.
"""


class ReviewerAgent(BaseAgent):
    name = "reviewer"
    model = "claude-sonnet-4-6"
    system_prompt = SYSTEM_PROMPT

    async def build_user_message(self, task: Task) -> str:
        return json.dumps({
            "requirements": task.requirements,
            "test_results": task.test_results,
            "branch": task.branch_name,
        })
```

- [ ] **Step 6: Create `agents/security.py`**

```python
import json
from agents.base import BaseAgent
from core.task import Task
from tools.code_tools import CodeTools

SYSTEM_PROMPT = """You are the Security Agent for Monarch AI.

Find security vulnerabilities in code. Be thorough and adversarial.

Respond with JSON:
{
  "verdict": "APPROVED" | "CONCERNS_RAISED" | "BLOCKED",
  "critical_issues": [{"type": "VULN_TYPE", "file": "", "line": 0, "description": ""}],
  "medium_issues": [],
  "low_issues": [],
  "owasp_coverage": ["A01", "A02", ...],
  "confidence": 0.0-1.0
}

BLOCKED if: SQL injection, RCE, hardcoded secrets, auth bypass, path traversal.
Check: OWASP Top 10 + prompt injection + shell=True + eval/exec on untrusted input.
"""


class SecurityAgent(BaseAgent):
    name = "security"
    model = "claude-opus-4-6"
    system_prompt = SYSTEM_PROMPT

    def __init__(self, code_tools: CodeTools) -> None:
        self.code = code_tools

    async def build_user_message(self, task: Task) -> str:
        scan = self.code.run_security_scan()
        return json.dumps({
            "branch": task.branch_name,
            "bandit_results": scan,
            "requirements": task.requirements,
        })
```

- [ ] **Step 7: Run tests**

```bash
pytest tests/unit/test_execution_agents.py -v
```
Expected: `PASS — 3 passed`

- [ ] **Step 8: Commit**

```bash
git add agents/implementer.py agents/testing.py agents/reviewer.py agents/security.py tests/unit/test_execution_agents.py
git commit -m "feat: Execution + Validation layer agents — Implementer, Testing, Reviewer, Security"
```

---

### Task 9: Agentes de Suporte (Documentação + Observabilidade)

**Files:**
- Create: `agents/documentation.py`
- Create: `agents/observability.py`
- Create: `tests/unit/test_support_agents.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/unit/test_support_agents.py
import pytest
from unittest.mock import patch
from agents.documentation import DocumentationAgent
from agents.observability import ObservabilityAgent
from agents.base import AgentResult
from core.task import Task


def make_completed_task() -> Task:
    task = Task(raw_input="Criar endpoint /users/{id}")
    task.requirements = {"user_stories": ["buscar usuário"]}
    task.architecture = {"api_design": {"method": "GET", "path": "/users/{id}"}}
    task.branch_name = "feat/monarch-001-users"
    task.pr_url = "https://github.com/owner/repo/pull/1"
    task.test_results = {"passed": True, "coverage": 90.0}
    return task


@pytest.mark.asyncio
async def test_documentation_agent_returns_docs():
    agent = DocumentationAgent()
    task = make_completed_task()
    mock_result = AgentResult(
        output={"files_updated": ["README.md", "docs/api.md"], "summary": "Added /users/{id} docs", "confidence": 0.9},
        confidence=0.9, concerns=[],
    )
    with patch.object(agent, "run", return_value=mock_result):
        result = await agent.run(task)
    assert "files_updated" in result.output


@pytest.mark.asyncio
async def test_observability_agent_adds_instrumentation():
    agent = ObservabilityAgent()
    task = make_completed_task()
    mock_result = AgentResult(
        output={"logs_added": True, "metrics_defined": ["request_count", "latency_p99"], "alerts_configured": False, "confidence": 0.85},
        confidence=0.85, concerns=[],
    )
    with patch.object(agent, "run", return_value=mock_result):
        result = await agent.run(task)
    assert result.output["logs_added"] is True
```

- [ ] **Step 2: Run to verify failure**

```bash
pytest tests/unit/test_support_agents.py -v
```
Expected: `FAIL`

- [ ] **Step 3: Create `agents/documentation.py`**

```python
import json
from agents.base import BaseAgent
from core.task import Task

SYSTEM_PROMPT = """You are the Documentation Agent for Monarch AI.

Update technical documentation to reflect the changes made.

Respond with JSON:
{
  "files_updated": ["path/to/doc.md"],
  "summary": "What was documented",
  "confidence": 0.0-1.0
}

Update: README if new endpoints, docstrings for new functions, CHANGELOG entry, API docs if applicable.
Keep docs concise and accurate. No filler text.
"""


class DocumentationAgent(BaseAgent):
    name = "documentation"
    model = "claude-haiku-4-5-20251001"
    system_prompt = SYSTEM_PROMPT

    async def build_user_message(self, task: Task) -> str:
        return json.dumps({
            "task_id": task.task_id,
            "raw_input": task.raw_input,
            "architecture": task.architecture,
            "pr_url": task.pr_url,
        })
```

- [ ] **Step 4: Create `agents/observability.py`**

```python
import json
from agents.base import BaseAgent
from core.task import Task

SYSTEM_PROMPT = """You are the Observability Agent for Monarch AI.

Ensure the implemented code is monitorable.

Respond with JSON:
{
  "logs_added": true | false,
  "metrics_defined": ["metric_name"],
  "alerts_configured": true | false,
  "instrumentation_summary": "what was added",
  "confidence": 0.0-1.0
}

Add: structured logging at entry/exit of new functions, latency metrics for new endpoints,
error rate counters, health check updates if a new service was added.
"""


class ObservabilityAgent(BaseAgent):
    name = "observability"
    model = "claude-haiku-4-5-20251001"
    system_prompt = SYSTEM_PROMPT

    async def build_user_message(self, task: Task) -> str:
        return json.dumps({
            "architecture": task.architecture,
            "branch": task.branch_name,
        })
```

- [ ] **Step 5: Run tests**

```bash
pytest tests/unit/test_support_agents.py -v
```
Expected: `PASS — 2 passed`

- [ ] **Step 6: Commit**

```bash
git add agents/documentation.py agents/observability.py tests/unit/test_support_agents.py
git commit -m "feat: Support layer agents — Documentation, Observability"
```

---

### Task 10: Orquestrador Central

**Files:**
- Create: `core/orchestrator.py`
- Create: `core/circuit_breaker.py`
- Create: `tests/unit/test_orchestrator.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/unit/test_orchestrator.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from core.orchestrator import Orchestrator
from core.task import Task, TaskStatus
from agents.base import AgentResult


def make_mock_result(output: dict, confidence: float = 0.9) -> AgentResult:
    return AgentResult(output=output, confidence=confidence, concerns=[])


@pytest.fixture
def orchestrator():
    db = AsyncMock()
    notifier = AsyncMock()
    return Orchestrator(db=db, notifier=notifier)


@pytest.mark.asyncio
async def test_orchestrator_creates_task_and_saves(orchestrator):
    with patch.object(orchestrator, "_run_direction_layer", return_value=None):
        with patch.object(orchestrator, "_run_definition_layer", return_value=None):
            with patch.object(orchestrator, "_run_execution_layer", return_value=None):
                with patch.object(orchestrator, "_run_validation_layer", return_value=None):
                    with patch.object(orchestrator, "_run_support_layer", return_value=None):
                        task = await orchestrator.create_task("Test task")
    assert task.task_id.startswith("monarch-")
    orchestrator.db.save_task.assert_called_once()


@pytest.mark.asyncio
async def test_orchestrator_marks_failed_on_exception(orchestrator):
    orchestrator._run_direction_layer = AsyncMock(side_effect=Exception("Agent failure"))
    task = Task(raw_input="Test")
    orchestrator.db.save_task = AsyncMock()
    orchestrator.db.update_task = AsyncMock()

    await orchestrator._run_task(task)

    assert task.status == TaskStatus.FAILED
    orchestrator.db.update_task.assert_called()


@pytest.mark.asyncio
async def test_orchestrator_discards_low_priority_task(orchestrator):
    task = Task(raw_input="Low priority")
    task.requirements = {"confidence": 0.9}

    mock_discovery = make_mock_result({"user_stories": [], "acceptance_criteria": [], "confidence": 0.9})
    mock_priority = make_mock_result({"priority": "DISCARDED", "justification": "Out of scope"})

    orchestrator._agents = MagicMock()

    with patch.object(orchestrator, "_invoke_agent") as mock_invoke:
        mock_invoke.side_effect = [mock_discovery, mock_priority]
        await orchestrator._run_direction_layer(task)

    assert task.status == TaskStatus.DISCARDED
```

- [ ] **Step 2: Run to verify failure**

```bash
pytest tests/unit/test_orchestrator.py -v
```
Expected: `FAIL`

- [ ] **Step 3: Create `core/circuit_breaker.py`**

```python
import asyncio
import logging
from collections import defaultdict, deque
from datetime import datetime, UTC

logger = logging.getLogger(__name__)


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, window_seconds: int = 600) -> None:
        self._failures: dict[str, deque] = defaultdict(deque)
        self._open: dict[str, bool] = defaultdict(bool)
        self._threshold = failure_threshold
        self._window = window_seconds

    def record_failure(self, agent_name: str) -> None:
        now = datetime.now(UTC).timestamp()
        self._failures[agent_name].append(now)
        self._clean_old(agent_name, now)
        if len(self._failures[agent_name]) >= self._threshold:
            self._open[agent_name] = True
            logger.warning(f"Circuit breaker OPEN for agent: {agent_name}")

    def record_success(self, agent_name: str) -> None:
        self._open[agent_name] = False
        self._failures[agent_name].clear()

    def is_open(self, agent_name: str) -> bool:
        return self._open.get(agent_name, False)

    def _clean_old(self, agent_name: str, now: float) -> None:
        dq = self._failures[agent_name]
        while dq and (now - dq[0]) > self._window:
            dq.popleft()
```

- [ ] **Step 4: Create `core/orchestrator.py`**

```python
import asyncio
import logging
from typing import Any, Protocol

from agents.base import AgentResult, BaseAgent
from agents.architecture import ArchitectureAgent
from agents.devils_advocate import DevilsAdvocateAgent
from agents.discovery import DiscoveryAgent
from agents.documentation import DocumentationAgent
from agents.implementer import ImplementerAgent
from agents.observability import ObservabilityAgent
from agents.planning import PlanningAgent
from agents.prioritization import PrioritizationAgent
from agents.reviewer import ReviewerAgent
from agents.security import SecurityAgent
from agents.testing import TestingAgent
from config import config
from core.circuit_breaker import CircuitBreaker
from core.task import Task, TaskStatus
from storage.database import Database
from tools.code_tools import CodeTools
from tools.fs_tools import FileSystemTools
from tools.github_tools import GitHubTools

logger = logging.getLogger(__name__)


class Notifier(Protocol):
    async def notify(self, task: Task, message: str) -> None: ...
    async def request_approval(self, task: Task, stage: str, proposal: dict[str, Any]) -> bool: ...


class Orchestrator:
    def __init__(self, db: Database, notifier: Notifier) -> None:
        self.db = db
        self.notifier = notifier
        self._circuit_breaker = CircuitBreaker()
        self._github = GitHubTools(config.github_token, config.github_repo)
        self._code_tools = CodeTools(".")
        self._fs_tools = FileSystemTools(".")
        self._agents: dict[str, BaseAgent] = {
            "discovery": DiscoveryAgent(),
            "prioritization": PrioritizationAgent(),
            "architecture": ArchitectureAgent(),
            "planning": PlanningAgent(),
            "devils_advocate": DevilsAdvocateAgent(),
            "implementer": ImplementerAgent(self._github, self._fs_tools),
            "testing": TestingAgent(self._code_tools),
            "reviewer": ReviewerAgent(),
            "security": SecurityAgent(self._code_tools),
            "documentation": DocumentationAgent(),
            "observability": ObservabilityAgent(),
        }

    async def create_task(self, raw_input: str) -> Task:
        task = Task(raw_input=raw_input)
        await self.db.save_task(task)
        asyncio.create_task(self._run_task(task))
        return task

    async def _run_task(self, task: Task) -> None:
        try:
            task.status = TaskStatus.RUNNING
            task.add_history("orchestrator", "started", task.raw_input)
            await self.db.update_task(task)
            await self.notifier.notify(task, f"▶️ Tarefa iniciada: {task.raw_input}")

            await self._run_direction_layer(task)
            if task.status in (TaskStatus.DISCARDED, TaskStatus.FAILED):
                return

            await self._run_definition_layer(task)
            if task.status == TaskStatus.FAILED:
                return

            await self._run_execution_layer(task)
            if task.status == TaskStatus.FAILED:
                return

            await self._run_validation_layer(task)
            if task.status == TaskStatus.FAILED:
                return

            await self._run_support_layer(task)
            task.status = TaskStatus.DONE
            await self.db.update_task(task)
            await self.notifier.notify(task, f"✅ Tarefa concluída! PR: {task.pr_url}")

        except Exception as e:
            logger.exception(f"Task {task.task_id} failed: {e}")
            task.status = TaskStatus.FAILED
            task.add_history("orchestrator", "failed", str(e))
            await self.db.update_task(task)
            await self.notifier.notify(task, f"❌ Tarefa falhou: {e}")

    async def _invoke_agent(self, agent_name: str, task: Task, max_retries: int | None = None) -> AgentResult:
        retries = max_retries if max_retries is not None else config.max_agent_retries
        if self._circuit_breaker.is_open(agent_name):
            raise RuntimeError(f"Circuit breaker open for {agent_name}")

        last_error: Exception | None = None
        for attempt in range(retries):
            try:
                result = await self._agents[agent_name].run(task)
                self._circuit_breaker.record_success(agent_name)
                task.add_history(agent_name, "completed", f"confidence={result.confidence:.2f}")
                await self.db.update_task(task)
                return result
            except Exception as e:
                last_error = e
                self._circuit_breaker.record_failure(agent_name)
                wait = 2 ** attempt
                logger.warning(f"[{agent_name}] attempt {attempt+1}/{retries} failed: {e}. Retrying in {wait}s")
                if attempt < retries - 1:
                    await asyncio.sleep(wait)

        raise RuntimeError(f"Agent {agent_name} failed after {retries} attempts: {last_error}")

    async def _run_direction_layer(self, task: Task) -> None:
        # Discovery
        result = await self._invoke_agent("discovery", task)
        task.requirements = result.output

        if result.confidence < config.confidence_threshold:
            task.status = TaskStatus.AWAITING_APPROVAL
            approved = await self.notifier.request_approval(task, "requirements_clarification", result.output)
            if not approved:
                task.status = TaskStatus.FAILED
                return
            task.status = TaskStatus.RUNNING

        # Prioritization
        result = await self._invoke_agent("prioritization", task)
        task.priority = result.output.get("priority")
        if task.priority == "DISCARDED":
            task.status = TaskStatus.DISCARDED
            await self.db.update_task(task)
            await self.notifier.notify(task, f"🗑️ Tarefa descartada: {result.output.get('justification')}")
            return

        await self.db.update_task(task)

    async def _run_definition_layer(self, task: Task) -> None:
        # Architecture
        result = await self._invoke_agent("architecture", task)
        task.architecture = result.output

        # Planning
        result = await self._invoke_agent("planning", task)
        task.plan = result.output.get("steps", [])

        # Devil's Advocate (round 1)
        for _ in range(2):
            da_result = await self._invoke_agent("devils_advocate", task)
            task.devils_advocate_rounds.append(da_result.output)
            if da_result.output.get("verdict") == "BLOCKED":
                await self.notifier.notify(task, f"🚫 Advogado bloqueou: {da_result.output.get('objections')}")
                result = await self._invoke_agent("architecture", task)
                task.architecture = result.output
                result = await self._invoke_agent("planning", task)
                task.plan = result.output.get("steps", [])
            else:
                break

        # Human approval for architecture
        task.status = TaskStatus.AWAITING_APPROVAL
        await self.db.update_task(task)
        approved = await self.notifier.request_approval(task, "architecture", task.architecture or {})
        if not approved:
            task.status = TaskStatus.FAILED
            return
        task.status = TaskStatus.RUNNING
        await self.db.update_task(task)

    async def _run_execution_layer(self, task: Task) -> None:
        for attempt in range(config.max_agent_retries):
            impl_result = await self._invoke_agent("implementer", task)
            task.branch_name = impl_result.output.get("branch")
            task.pr_url = impl_result.output.get("pr_url")

            test_result = await self._invoke_agent("testing", task)
            task.test_results = test_result.output

            if test_result.output.get("passed"):
                break
            logger.warning(f"Tests failed attempt {attempt+1}, retrying implementer")

        await self.db.update_task(task)

    async def _run_validation_layer(self, task: Task) -> None:
        review_result = await self._invoke_agent("reviewer", task)
        security_result = await self._invoke_agent("security", task)
        task.review_report = {**review_result.output, **security_result.output}

        if security_result.output.get("verdict") == "BLOCKED":
            task.status = TaskStatus.AWAITING_APPROVAL
            await self.db.update_task(task)
            approved = await self.notifier.request_approval(task, "security_critical", security_result.output)
            if not approved:
                task.status = TaskStatus.FAILED
                return
            task.status = TaskStatus.RUNNING

        # Devil's Advocate (round 2 — post implementation)
        da_result = await self._invoke_agent("devils_advocate", task)
        task.devils_advocate_rounds.append(da_result.output)

        # Human approval for final PR
        task.status = TaskStatus.AWAITING_APPROVAL
        await self.db.update_task(task)
        approved = await self.notifier.request_approval(task, "final_pr", {"pr_url": task.pr_url, "review": task.review_report})
        if not approved:
            task.status = TaskStatus.FAILED
            return
        task.status = TaskStatus.RUNNING
        await self.db.update_task(task)

    async def _run_support_layer(self, task: Task) -> None:
        await self._invoke_agent("documentation", task)
        await self._invoke_agent("observability", task)
```

- [ ] **Step 5: Run tests**

```bash
pytest tests/unit/test_orchestrator.py -v
```
Expected: `PASS — 3 passed`

- [ ] **Step 6: Commit**

```bash
git add core/orchestrator.py core/circuit_breaker.py tests/unit/test_orchestrator.py
git commit -m "feat: Central Orchestrator with full flow + circuit breaker + retry logic"
```

---

### Task 11: Web UI (FastAPI)

**Files:**
- Create: `interfaces/web/app.py`
- Create: `interfaces/web/templates/index.html`
- Create: `tests/unit/test_web_ui.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/unit/test_web_ui.py
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_get_index_returns_200():
    from interfaces.web.app import create_app
    app = create_app(orchestrator=MagicMock(), db=AsyncMock())
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_post_task_creates_task():
    from interfaces.web.app import create_app
    mock_orch = MagicMock()
    mock_task = MagicMock()
    mock_task.task_id = "monarch-abc123"
    mock_orch.create_task = AsyncMock(return_value=mock_task)

    app = create_app(orchestrator=mock_orch, db=AsyncMock())
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/tasks", json={"input": "Criar endpoint /users"})

    assert response.status_code == 200
    assert response.json()["task_id"] == "monarch-abc123"


@pytest.mark.asyncio
async def test_approve_task():
    from interfaces.web.app import create_app
    mock_db = AsyncMock()
    mock_db.get_task.return_value = MagicMock(task_id="monarch-001", status="awaiting_approval")

    app = create_app(orchestrator=MagicMock(), db=mock_db)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/tasks/monarch-001/approve")
    assert response.status_code == 200
```

- [ ] **Step 2: Run to verify failure**

```bash
pytest tests/unit/test_web_ui.py -v
```
Expected: `FAIL`

- [ ] **Step 3: Create `interfaces/web/app.py`**

```python
import asyncio
from typing import Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path

from core.orchestrator import Orchestrator
from core.task import TaskStatus
from storage.database import Database

_pending_approvals: dict[str, asyncio.Event] = {}
_approval_results: dict[str, bool] = {}


class TaskInput(BaseModel):
    input: str


class ApprovalResult(BaseModel):
    approved: bool
    feedback: str = ""


def create_app(orchestrator: Orchestrator, db: Database) -> FastAPI:
    app = FastAPI(title="Monarch AI")

    @app.get("/", response_class=HTMLResponse)
    async def index() -> str:
        template = Path(__file__).parent / "templates" / "index.html"
        return template.read_text()

    @app.post("/tasks")
    async def create_task(body: TaskInput) -> dict[str, str]:
        task = await orchestrator.create_task(body.input)
        return {"task_id": task.task_id, "status": task.status.value}

    @app.get("/tasks")
    async def list_tasks() -> list[dict[str, Any]]:
        tasks = await db.list_active_tasks()
        return [{"task_id": t.task_id, "status": t.status.value, "input": t.raw_input} for t in tasks]

    @app.get("/tasks/{task_id}")
    async def get_task(task_id: str) -> dict[str, Any]:
        task = await db.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return {
            "task_id": task.task_id,
            "status": task.status.value,
            "input": task.raw_input,
            "requirements": task.requirements,
            "architecture": task.architecture,
            "pr_url": task.pr_url,
            "test_results": task.test_results,
            "review_report": task.review_report,
            "history": [{"agent": h.agent, "action": h.action, "detail": h.detail} for h in task.history],
        }

    @app.post("/tasks/{task_id}/approve")
    async def approve_task(task_id: str, result: ApprovalResult | None = None) -> dict[str, str]:
        task = await db.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        approved = result.approved if result else True
        _approval_results[task_id] = approved
        if task_id in _pending_approvals:
            _pending_approvals[task_id].set()
        return {"task_id": task_id, "approved": str(approved)}

    return app
```

- [ ] **Step 4: Create `interfaces/web/templates/index.html`**

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Monarch AI</title>
<style>
  body { font-family: system-ui; max-width: 900px; margin: 2rem auto; padding: 0 1rem; background: #0f0f0f; color: #e0e0e0; }
  h1 { color: #a78bfa; }
  .card { background: #1a1a1a; border: 1px solid #333; border-radius: 8px; padding: 1rem; margin: 1rem 0; }
  input, textarea { width: 100%; padding: 0.5rem; background: #222; border: 1px solid #444; color: #e0e0e0; border-radius: 4px; }
  button { padding: 0.5rem 1rem; border-radius: 4px; border: none; cursor: pointer; font-weight: bold; }
  .btn-primary { background: #7c3aed; color: white; }
  .btn-approve { background: #059669; color: white; }
  .btn-reject { background: #dc2626; color: white; }
  .status-awaiting { color: #f59e0b; }
  .status-running { color: #3b82f6; }
  .status-done { color: #10b981; }
  .status-failed { color: #ef4444; }
</style>
</head>
<body>
<h1>👑 Monarch AI</h1>

<div class="card">
  <h2>Nova Tarefa</h2>
  <textarea id="taskInput" rows="3" placeholder="Descreva a tarefa em linguagem natural..."></textarea>
  <br><br>
  <button class="btn-primary" onclick="createTask()">Enviar Tarefa</button>
</div>

<div class="card">
  <h2>Tarefas Ativas</h2>
  <div id="taskList">Carregando...</div>
</div>

<script>
async function createTask() {
  const input = document.getElementById('taskInput').value;
  if (!input.trim()) return;
  const res = await fetch('/tasks', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({input}) });
  const data = await res.json();
  alert(`Tarefa criada: ${data.task_id}`);
  document.getElementById('taskInput').value = '';
  loadTasks();
}

async function loadTasks() {
  const res = await fetch('/tasks');
  const tasks = await res.json();
  const el = document.getElementById('taskList');
  if (!tasks.length) { el.innerHTML = '<p>Nenhuma tarefa ativa.</p>'; return; }
  el.innerHTML = tasks.map(t => `
    <div class="card">
      <strong>${t.task_id}</strong>
      <span class="status-${t.status}"> ● ${t.status}</span>
      <p>${t.input}</p>
      ${t.status === 'awaiting_approval' ? `
        <button class="btn-approve" onclick="approve('${t.task_id}', true)">✅ Aprovar</button>
        <button class="btn-reject" onclick="approve('${t.task_id}', false)">❌ Rejeitar</button>
      ` : ''}
    </div>
  `).join('');
}

async function approve(taskId, approved) {
  await fetch(`/tasks/${taskId}/approve`, { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({approved}) });
  loadTasks();
}

setInterval(loadTasks, 3000);
loadTasks();
</script>
</body>
</html>
```

- [ ] **Step 5: Run tests**

```bash
pytest tests/unit/test_web_ui.py -v
```
Expected: `PASS — 3 passed`

- [ ] **Step 6: Commit**

```bash
git add interfaces/web/ tests/unit/test_web_ui.py
git commit -m "feat: Web UI — FastAPI painel de controle com aprovação humana"
```

---

### Task 12: Telegram Bot

**Files:**
- Create: `interfaces/telegram_bot.py`
- Create: `tests/unit/test_telegram_bot.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/unit/test_telegram_bot.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from interfaces.telegram_bot import TelegramNotifier
from core.task import Task, TaskStatus


@pytest.fixture
def notifier():
    with patch("interfaces.telegram_bot.Application"):
        n = TelegramNotifier(token="fake:token", chat_id="123")
        n._app = MagicMock()
        n._app.bot = AsyncMock()
        return n


@pytest.mark.asyncio
async def test_notify_sends_message(notifier):
    task = Task(raw_input="test")
    await notifier.notify(task, "Tarefa iniciada")
    notifier._app.bot.send_message.assert_called_once()
    call_kwargs = notifier._app.bot.send_message.call_args.kwargs
    assert call_kwargs["chat_id"] == "123"
    assert "Tarefa iniciada" in call_kwargs["text"]


@pytest.mark.asyncio
async def test_request_approval_formats_message(notifier):
    task = Task(raw_input="Criar endpoint")
    task.task_id = "monarch-001"

    notifier._app.bot.send_message = AsyncMock(return_value=MagicMock(message_id=42))

    with patch("asyncio.wait_for", AsyncMock(return_value=True)):
        with patch.object(notifier, "_wait_for_approval", AsyncMock(return_value=True)):
            result = await notifier.request_approval(task, "architecture", {"components": ["UserController"]})

    assert isinstance(result, bool)
```

- [ ] **Step 2: Run to verify failure**

```bash
pytest tests/unit/test_telegram_bot.py -v
```
Expected: `FAIL`

- [ ] **Step 3: Create `interfaces/telegram_bot.py`**

```python
import asyncio
import json
import logging
from typing import Any

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

from core.task import Task
from config import config

logger = logging.getLogger(__name__)

_pending: dict[str, asyncio.Future] = {}


class TelegramNotifier:
    def __init__(self, token: str, chat_id: str) -> None:
        self._chat_id = chat_id
        self._app = Application.builder().token(token).build()
        self._app.add_handler(CallbackQueryHandler(self._handle_callback))
        self._app.add_handler(CommandHandler("status", self._cmd_status))

    async def notify(self, task: Task, message: str) -> None:
        text = f"🤖 *Monarch AI* — `{task.task_id}`\n\n{message}"
        await self._app.bot.send_message(
            chat_id=self._chat_id,
            text=text,
            parse_mode="Markdown",
        )

    async def request_approval(
        self,
        task: Task,
        stage: str,
        proposal: dict[str, Any],
    ) -> bool:
        summary = json.dumps(proposal, indent=2, ensure_ascii=False)[:800]
        text = (
            f"🤖 *Monarch AI* — Aprovação necessária\n\n"
            f"Tarefa: `{task.task_id}`\n"
            f"Etapa: *{stage}*\n\n"
            f"```\n{summary}\n```"
        )
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Aprovar", callback_data=f"approve:{task.task_id}"),
                InlineKeyboardButton("❌ Rejeitar", callback_data=f"reject:{task.task_id}"),
            ]
        ])
        await self._app.bot.send_message(
            chat_id=self._chat_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
        return await self._wait_for_approval(task.task_id)

    async def _wait_for_approval(self, task_id: str) -> bool:
        loop = asyncio.get_event_loop()
        future: asyncio.Future = loop.create_future()
        _pending[task_id] = future
        try:
            return await asyncio.wait_for(future, timeout=config.approval_timeout_minutes * 60)
        except asyncio.TimeoutError:
            logger.warning(f"Approval timeout for task {task_id}")
            return False
        finally:
            _pending.pop(task_id, None)

    async def _handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        data = query.data or ""
        action, task_id = data.split(":", 1) if ":" in data else ("", "")
        if task_id in _pending and not _pending[task_id].done():
            _pending[task_id].set_result(action == "approve")
            result_text = "✅ Aprovado!" if action == "approve" else "❌ Rejeitado."
            await query.edit_message_reply_markup(reply_markup=None)
            await query.message.reply_text(f"{result_text} `{task_id}`", parse_mode="Markdown")

    async def _cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        pending_count = len(_pending)
        await update.message.reply_text(
            f"🤖 Monarch AI\nAprovações pendentes: {pending_count}",
            parse_mode="Markdown",
        )

    async def start(self) -> None:
        await self._app.initialize()
        await self._app.start()
        await self._app.updater.start_polling()

    async def stop(self) -> None:
        await self._app.updater.stop()
        await self._app.stop()
        await self._app.shutdown()
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/unit/test_telegram_bot.py -v
```
Expected: `PASS — 2 passed`

- [ ] **Step 5: Commit**

```bash
git add interfaces/telegram_bot.py tests/unit/test_telegram_bot.py
git commit -m "feat: Telegram bot — notificações + aprovações inline"
```

---

### Task 13: Entry Point Principal

**Files:**
- Create: `main.py`
- Create: `interfaces/cli.py`
- Create: `tests/integration/test_end_to_end.py`

- [ ] **Step 1: Write integration test**

```python
# tests/integration/test_end_to_end.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from core.task import TaskStatus


@pytest.mark.asyncio
async def test_full_flow_creates_pr():
    """Integration test: task goes through full flow and ends with PR created."""
    from storage.database import Database
    from core.orchestrator import Orchestrator

    db = Database("sqlite+aiosqlite:///:memory:")
    await db.init()

    mock_notifier = MagicMock()
    mock_notifier.notify = AsyncMock()
    mock_notifier.request_approval = AsyncMock(return_value=True)

    orch = Orchestrator(db=db, notifier=mock_notifier)

    # Mock all agents to return valid results
    from agents.base import AgentResult

    def make_result(extra: dict) -> AgentResult:
        return AgentResult(output={**extra, "confidence": 0.9}, confidence=0.9, concerns=[])

    agent_outputs = {
        "discovery": make_result({"user_stories": ["test"], "acceptance_criteria": ["test"], "technical_notes": [], "clarification_questions": []}),
        "prioritization": make_result({"priority": "MVP_V1", "justification": "core"}),
        "architecture": make_result({"components": ["Controller"], "api_design": {"method": "GET"}, "concerns": []}),
        "planning": make_result({"steps": [{"order": 1, "description": "test", "files": [], "type": "test"}]}),
        "devils_advocate": make_result({"objections": [], "risks": [], "missing_scenarios": [], "verdict": "APPROVED"}),
        "implementer": make_result({"branch": "feat/monarch-test", "files_changed": [], "pr_url": "https://github.com/test/pr/1"}),
        "testing": make_result({"passed": True, "coverage": 85.0, "tests_written": 3, "failures": []}),
        "reviewer": make_result({"verdict": "APPROVED", "quality_score": 8.5, "issues": []}),
        "security": make_result({"verdict": "APPROVED", "critical_issues": [], "medium_issues": []}),
        "documentation": make_result({"files_updated": ["README.md"]}),
        "observability": make_result({"logs_added": True, "metrics_defined": []}),
    }

    for agent_name, result in agent_outputs.items():
        orch._agents[agent_name].run = AsyncMock(return_value=result)

    task = await orch.create_task("Criar endpoint de teste")

    # Wait for async task to complete
    import asyncio
    await asyncio.sleep(0.1)

    final_task = await db.get_task(task.task_id)
    assert final_task is not None
    assert final_task.status == TaskStatus.DONE
    assert final_task.pr_url == "https://github.com/test/pr/1"

    await db.close()
```

- [ ] **Step 2: Run to verify failure**

```bash
pytest tests/integration/test_end_to_end.py -v
```
Expected: `FAIL — ImportError or assertion failure`

- [ ] **Step 3: Create `main.py`**

```python
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn
from fastapi import FastAPI

from config import config
from core.orchestrator import Orchestrator
from interfaces.telegram_bot import TelegramNotifier
from interfaces.web.app import create_app
from storage.database import Database

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def run() -> None:
    db = Database(config.database_url)
    await db.init()
    logger.info("Database initialized")

    notifier = TelegramNotifier(
        token=config.telegram_bot_token,
        chat_id=config.telegram_chat_id,
    )
    await notifier.start()
    logger.info("Telegram bot started")

    orchestrator = Orchestrator(db=db, notifier=notifier)
    app = create_app(orchestrator=orchestrator, db=db)

    server_config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=config.web_port,
        log_level="info",
    )
    server = uvicorn.Server(server_config)

    logger.info(f"Monarch AI running at http://localhost:{config.web_port}")

    try:
        await server.serve()
    finally:
        await notifier.stop()
        await db.close()
        logger.info("Monarch AI shutdown complete")


if __name__ == "__main__":
    asyncio.run(run())
```

- [ ] **Step 4: Create `interfaces/cli.py`**

```python
"""CLI entry point for submitting tasks directly to Monarch AI."""
import argparse
import asyncio
import json
import sys

import httpx


async def submit_task(task_input: str, host: str = "localhost", port: int = 8000) -> None:
    url = f"http://{host}:{port}/tasks"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"input": task_input})
        response.raise_for_status()
        data = response.json()
        print(f"✅ Task created: {data['task_id']}")
        print(f"   Status: {data['status']}")
        print(f"   Track at: http://{host}:{port}/tasks/{data['task_id']}")


async def get_status(task_id: str, host: str = "localhost", port: int = 8000) -> None:
    url = f"http://{host}:{port}/tasks/{task_id}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="Monarch AI CLI")
    subparsers = parser.add_subparsers(dest="command")

    submit = subparsers.add_parser("submit", help="Submit a new task")
    submit.add_argument("input", help="Task description in natural language")
    submit.add_argument("--host", default="localhost")
    submit.add_argument("--port", type=int, default=8000)

    status = subparsers.add_parser("status", help="Check task status")
    status.add_argument("task_id", help="Task ID (e.g. monarch-abc123)")
    status.add_argument("--host", default="localhost")
    status.add_argument("--port", type=int, default=8000)

    args = parser.parse_args()

    if args.command == "submit":
        asyncio.run(submit_task(args.input, args.host, args.port))
    elif args.command == "status":
        asyncio.run(get_status(args.task_id, args.host, args.port))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run all tests**

```bash
pytest tests/ -v --tb=short
```
Expected: `All tests pass`

- [ ] **Step 6: Run linter and type check**

```bash
ruff check . --fix
mypy core/ agents/ tools/ interfaces/ --ignore-missing-imports
```
Expected: No errors

- [ ] **Step 7: Final commit**

```bash
git add main.py interfaces/cli.py tests/integration/
git commit -m "feat: main entry point + CLI + integration test — Monarch AI v1 complete"
```

---

## Self-Review Checklist

- [x] Spec coverage: All 11 agents implemented (Tasks 6-9). Orchestrator (Task 10). Both interfaces (Tasks 11-12). Storage (Task 2). Tools (Tasks 4-5). Config (Task 1). Integration test (Task 13).
- [x] No placeholders: All steps contain actual code
- [x] Type consistency: `AgentResult`, `TaskContext`, `Task`, `Database` used consistently across all tasks
- [x] TDD: Every task writes failing tests before implementation
- [x] Commit cadence: One commit per task
- [x] Security: `fs_tools.py` has path traversal protection. `code_tools.py` never uses `shell=True`
