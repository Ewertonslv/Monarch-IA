---
name: gh-fix-ci
description: "Debug and fix failing GitHub Actions checks on a PR. Use when a CI pipeline fails after the Implementer Agent creates a PR — diagnoses the root cause and fixes it before requesting human review."
---

# GitHub CI Fix

Debug and resolve failing GitHub Actions checks using the `gh` CLI.

## When to Use

- After Agente Implementador creates a PR and CI fails
- When pytest/linting/type-checking fails in the pipeline
- Before requesting human code review (never present a PR with red CI)

## Diagnostic Process

```bash
# 1. Get PR status
gh pr checks <pr-number> --watch

# 2. List failed jobs
gh run list --branch <branch> --limit 5

# 3. Get full logs of the failing run
gh run view <run-id> --log-failed

# 4. View specific job logs
gh run view <run-id> --job <job-id> --log
```

## Common Failure Patterns & Fixes

### Import errors / ModuleNotFoundError
```bash
# Check if dependency is in requirements
grep -r "import X" src/
# Fix: add to requirements.txt or pyproject.toml
```

### Pytest failures
```bash
# Run locally first to reproduce
pytest tests/ -x -v 2>&1 | head -50
# Fix the failing test or the implementation
```

### Type errors (mypy)
```bash
mypy src/ --ignore-missing-imports
```

### Linting (ruff/flake8)
```bash
ruff check src/ --fix
```

## Fix → Verify → Push Loop

```bash
# Fix the issue locally
# Run the exact command from CI
pytest tests/ -x
# Push fix
git add -A && git commit -m "fix: resolve CI failure - <description>"
git push
# Wait for CI
gh pr checks <pr-number> --watch
```

## Hard Rules

- NEVER mark a task complete while CI is red
- NEVER skip CI with `--no-verify`
- Always reproduce locally before pushing a fix
- If CI fails 3 times on same issue → escalate to human
