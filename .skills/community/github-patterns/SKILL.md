---
name: github-patterns
description: "GitHub PR, code review, and branching patterns for multi-agent systems. Use when the Implementer Agent creates branches/PRs or when preparing code for human review."
---

# GitHub Patterns for Multi-Agent Development

Best practices for branching, PRs, and code review in an AI-driven development workflow.

## Branch Naming Convention

```
feat/monarch-<task-id>-<short-description>
fix/monarch-<task-id>-<short-description>
refactor/monarch-<task-id>-<short-description>
```

Examples:
```
feat/monarch-42-discovery-agent
fix/monarch-15-orchestrator-retry-logic
```

## Creating a PR (Implementer Agent Pattern)

```bash
# 1. Create branch from main
git checkout -b feat/monarch-<id>-<description> main

# 2. Implement + commit (TDD cycle)
git add src/ tests/
git commit -m "feat: <what and why>"

# 3. Push
git push -u origin feat/monarch-<id>-<description>

# 4. Create PR
gh pr create \
  --title "feat: <short description>" \
  --body "$(cat <<'EOF'
## What

<1-2 sentences>

## Why

<motivation from task context>

## Test Plan

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] CI green

## Agent Notes

Task ID: monarch-<id>
Agents involved: <list>
Human approval required: <yes/no>
EOF
)" \
  --label "ai-generated" \
  --draft
```

## PR States for Monarch AI

| State | Meaning | Next Action |
|-------|---------|-------------|
| Draft | Agente still working | Wait |
| Open (CI red) | Fix CI first | Run gh-fix-ci skill |
| Open (CI green) | Ready for human review | Notify via Telegram |
| Changes requested | Human left feedback | Agente Revisor processes |
| Approved | Ready to merge | Human merges (never auto-merge to main) |

## Code Review Response Pattern

When human leaves review comments:
```bash
# View comments
gh pr view <pr-number> --comments

# Address each comment, commit
git add <files>
git commit -m "review: address feedback - <summary>"
git push

# Re-request review
gh pr review <pr-number> --request-review <reviewer>
```

## Branch Protection Rules (Recommend for main)

- Require PR before merging
- Require CI to pass
- Require at least 1 human approval
- No force push
- No auto-merge for AI-generated PRs touching critical files

## Useful gh Commands for Monarch AI

```bash
# List open AI-generated PRs
gh pr list --label "ai-generated"

# Check PR CI status
gh pr checks <pr-number>

# View PR diff
gh pr diff <pr-number>

# Merge (human action only)
gh pr merge <pr-number> --squash --delete-branch
```
