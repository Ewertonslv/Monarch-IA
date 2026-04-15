# Monarch AI — Project Reference

Multi-agent system that automates SaaS software development. Receives a task in natural
language and delivers a tested GitHub PR with minimal human intervention.

**Stack:** Python 3.14, Anthropic SDK (Claude), FastAPI, Telegram Bot, SQLite (aiosqlite),
PyGithub, pytest, pydantic-settings.

---

## Running the System

```bash
# Start web panel (localhost:8000) + Telegram bot
python main.py

# CLI — submit a task with auto-approval
python -m interfaces.cli run "Create a login endpoint with JWT auth"

# Run all tests
python -m pytest

# Run a specific test file
python -m pytest tests/unit/test_orchestrator.py -v
```

---

## Configuration

All config lives in `config.py` (pydantic-settings). Requires a `.env` file or
environment variables:

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `GITHUB_TOKEN` | GitHub personal access token |
| `GITHUB_REPO` | Target repo in `owner/repo` format |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | Telegram chat ID that receives approvals |
| `WEB_PORT` | Web panel port (default: 8000) |
| `DATABASE_URL` | SQLite URL (default: `sqlite+aiosqlite:///./monarch_ai.db`) |
| `MAX_AGENT_RETRIES` | Retries per agent before circuit opens (default: 3) |
| `CONFIDENCE_THRESHOLD` | Minimum agent confidence (default: 0.70) |

---

## Architecture

```
main.py                    ← Entry point: starts web + Telegram concurrently
config.py                  ← pydantic-settings Config singleton
core/
  task.py                  ← Task dataclass + TaskStatus enum + HistoryEntry
  orchestrator.py          ← Central coordinator: runs the 11-agent pipeline
  circuit_breaker.py       ← Per-agent fault isolation (CLOSED/OPEN/HALF_OPEN)
agents/
  base.py                  ← Abstract BaseAgent with Anthropic tool_use loop + prompt caching
  discovery.py             ← Layer 1 — Direction: understands the raw request
  prioritization.py        ← Layer 2 — Definition: assesses business priority
  architecture.py          ← Layer 2 — Definition: designs technical solution
  planning.py              ← Layer 2 — Definition: creates step-by-step plan
  devils_advocate.py       ← Layer 2 — Definition: challenges plan before implementation
  implementer.py           ← Layer 3 — Execution: writes code via GitHub tools
  testing.py               ← Layer 3 — Execution: analyses pytest/ruff/mypy/bandit results
  reviewer.py              ← Layer 3 — Execution: reviews PR diff
  security.py              ← Layer 3 — Execution: OWASP security review
  deploy.py                ← Layer 3 — Execution: generates CI/CD workflow + deployment config
  documentation.py         ← Layer 4 — Support: generates changelog + docs
  observability.py         ← Layer 4 — Support: recommends metrics + alerts
tools/
  github_tools.py          ← PyGithub wrapper: read_file, list_files, write_file,
                              create_branch, create_pr, get_pr_diff, as_tools_schema()
  code_tools.py            ← Subprocess runners: run_pytest, run_ruff, run_mypy,
                              run_bandit, run_all_checks
  fs_tools.py              ← Local filesystem helpers: read, write, delete, list, exists
storage/
  database.py              ← Async SQLite via SQLAlchemy: init, save_task, update_task,
                              get_task, list_active_tasks, close
  models.py                ← SQLAlchemy ORM model TaskRecord
interfaces/
  web/
    app.py                 ← FastAPI app: REST endpoints + WebSocket for real-time updates
    templates/index.html   ← Single-page web panel (dark theme, auto-approve buttons)
  telegram_bot.py          ← Telegram bot: task submission + inline approval keyboard
  cli.py                   ← CLI: `monarch run "..."` with auto-approval
```

---

## Pipeline Flow

```
Task created
    │
    ▼
[Discovery]          → task.requirements
    │
[Prioritization]     → task.priority
    │
[Architecture]       → task.architecture
    │
[Planning]           → task.plan, task.branch_name
    │
[Devil's Advocate]   → task.devils_advocate_rounds (up to 2 rounds)
    │ if issues: re-runs Architecture + Planning
    │
[APPROVAL GATE 1]    ← Telegram/web: Approve or Reject
    │
[create_branch]      → GitHub branch created
    │
[Implementer]        → writes files to GitHub branch
    │
[Testing]            → task.test_results (pytest/ruff/mypy/bandit)
    │
[Reviewer]           → task.review_report
    │
[Security]           → task.security_report
    │
[Deploy]             → task.deploy_report, writes .github/workflows/ci.yml to branch
    │
[create_pr]          → task.pr_url (if review + security approved)
    │
[APPROVAL GATE 2]    ← Telegram/web: Approve or Reject
    │
[Documentation]      → changelog entry, README sections
    │
[Observability]      → metrics, alerts, tracing suggestions
    │
    ▼
Task DONE
```

---

## Agent Models

| Agent | Model | Reason |
|---|---|---|
| Discovery | claude-opus-4-6 | Critical: shapes the entire pipeline |
| Architecture | claude-opus-4-6 | Critical: technical design decisions |
| Planning | claude-opus-4-6 | Critical: step-by-step implementation plan |
| Devil's Advocate | claude-opus-4-6 | Critical: must find real issues |
| Implementer | claude-opus-4-6 | Critical: writes production code |
| Reviewer | claude-opus-4-6 | Critical: code quality gate |
| Security | claude-opus-4-6 | Critical: security gate |
| Deploy | claude-sonnet-4-6 | Standard: CI/CD config generation |
| Prioritization | claude-sonnet-4-6 | Standard: priority assessment |
| Testing | claude-sonnet-4-6 | Standard: interprets test output |
| Documentation | claude-haiku-4-5-20251001 | Mechanical: structured doc generation |
| Observability | claude-haiku-4-5-20251001 | Mechanical: structured recommendations |

---

## Task State

```python
class TaskStatus(str, Enum):
    PENDING            = "pending"
    RUNNING            = "running"
    AWAITING_APPROVAL  = "awaiting_approval"
    DONE               = "done"
    FAILED             = "failed"
    DISCARDED          = "discarded"
```

Key fields on `Task`:
- `task_id` — `monarch-{8hex}` (e.g. `monarch-a3f2c8b1`)
- `requirements` — set by Discovery
- `priority` — set by Prioritization
- `architecture` — set by Architecture
- `plan` — list of steps, set by Planning
- `branch_name` — set by Planning
- `devils_advocate_rounds` — list of review rounds
- `pr_url` — set by Orchestrator after create_pr
- `test_results` — set by Testing agent
- `review_report` — set by Reviewer agent
- `security_report` — set by Security agent
- `deploy_report` — set by Deploy agent (project_type, deployment_target, files_written)
- `history` — list of `HistoryEntry(agent, action, detail, timestamp)`

---

## Tests

```
tests/
  conftest.py                        ← Sets env vars before any import
  unit/
    test_task.py                     ← Task dataclass + status transitions (4 tests)
    test_config.py                   ← Config validation (2 tests)
    test_storage.py                  ← Database CRUD (5 tests)
    test_base_agent.py               ← BaseAgent: tool_use loop, JSON extraction (4 tests)
    test_github_tools.py             ← GitHubTools all methods mocked (8 tests)
    test_code_tools.py               ← CodeTools subprocess wrappers (8 tests)
    test_fs_tools.py                 ← FsTools filesystem ops (6 tests)
    test_discovery_agent.py          ← DiscoveryAgent (4 tests)
    test_definition_agents.py        ← Prioritization, Architecture, Planning, DA (9 tests)
    test_execution_agents.py         ← Implementer, Testing, Reviewer, Security (9 tests)
    test_deploy_agent.py             ← DeployAgent: CI workflow generation (5 tests)
    test_support_agents.py           ← Documentation, Observability (6 tests)
    test_circuit_breaker.py          ← CircuitBreaker state machine (6 tests)
    test_orchestrator.py             ← Orchestrator pipeline (3 tests)
    test_web_app.py                  ← FastAPI endpoints (6 tests)
    test_telegram_bot.py             ← Telegram bot commands + callbacks (7 tests)
  integration/
    test_pipeline_integration.py     ← Full 11-agent pipeline, mocked at Claude API (2 tests)

Total: 94 tests
```

---

## Key Design Decisions

- **No LangChain/CrewAI** — pure Anthropic SDK for full control and optimal prompt caching
- **Prompt caching** — all system prompts use `cache_control: {"type": "ephemeral"}` (~80% cost reduction on repeated calls)
- **tool_use loop** — BaseAgent loops until `stop_reason != "tool_use"` before extracting JSON
- **All agents return JSON** — structured output via system prompt instruction, parsed by `_extract_json()` (handles markdown code fences)
- **Circuit breaker per agent** — isolates failures, prevents cascading; auto-recovers after `recovery_timeout`
- **Two human approval gates** — post-planning (before any code is written) and post-implementation (before docs/observability)
- **Task is the single source of truth** — every agent reads from and writes to `Task`, persisted to SQLite

---

## Skills Available

Skills extend Claude Code's capabilities. Invoke with `/skill-name` or reference them
explicitly when the task matches.

### Core Superpowers (`expxagents/node_modules/superpowers/skills/`)

| Skill | When to use |
|---|---|
| `brainstorming` | Exploring new features, architecture decisions, problem-solving |
| `writing-plans` | Before implementing anything non-trivial — produces a step-by-step plan |
| `executing-plans` | Working through a written plan task by task |
| `test-driven-development` | Adding any new agent, tool, or feature (Red → Green → Refactor) |
| `systematic-debugging` | When a pipeline run fails and the cause isn't obvious |
| `finishing-a-development-branch` | Before opening a PR — ensures branch is clean and ready |
| `requesting-code-review` | After implementation, before merging |
| `receiving-code-review` | Processing review feedback and applying fixes |
| `dispatching-parallel-agents` | Running multiple independent tasks simultaneously |
| `subagent-driven-development` | Delegating complex research/implementation to subagents |
| `using-git-worktrees` | Parallel branches without context switching |
| `verification-before-completion` | Final check before declaring a task done |
| `using-superpowers` | Meta-skill: how to use the skills system itself |
| `writing-skills` | Creating new custom skills for this project |

### Superpowers Lab (`.skills/superpowers-lab/`) — Experimental

| Skill | When to use |
|---|---|
| `finding-duplicate-functions` | Before adding new utilities — checks for existing implementations |
| `mcp-cli` | Interacting with MCP servers from the CLI |
| `using-tmux-for-interactive-commands` | Running long pipeline processes in background panes |

### Community Custom (`.skills/community/`) — Project-specific

| Skill | When to use |
|---|---|
| `security-review` | Before merging any PR that touches agent tools, external API calls, or credential handling. OWASP Top 10 + AI-specific risks |
| `gh-fix-ci` | When a GitHub Actions CI check fails after the Implementer Agent creates a PR |
| `github-patterns` | When working with branches/PRs in the multi-agent context |

### Skills Config (`opencode.json`)

```json
{
  "skills": {
    "paths": [
      "D:/Users/Ewerton-viggo/Documents/expxagents/node_modules/superpowers/skills",
      "D:/Users/Ewerton-viggo/Documents/Monarch AI/.skills/superpowers-lab",
      "D:/Users/Ewerton-viggo/Documents/Monarch AI/.skills/community"
    ]
  }
}
```

---

## Known Issues / TODO

- `TestingAgent` class name triggers a pytest collection warning (not a failure)
- `ImplementerAgent.execute_tool` handles `branch` as a popped key from inputs — validate behavior in real runs
- Approval timeout is 5 minutes (`_APPROVAL_TIMEOUT_SECONDS = 300`) — ajustar se necessário
