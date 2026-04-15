---
name: security-review
description: "Security-focused code review for Python AI agent systems. Use before merging any PR that touches agent tools, external API calls, credential handling, or code execution. Checks OWASP Top 10 + AI-specific risks."
---

# Security Review for AI Agent Systems

Specialized security review for Python-based multi-agent systems. Goes beyond standard OWASP to cover AI-specific attack surfaces.

## When to Use

- Before merging any PR from the Agente Implementador
- When adding new tools (GitHub tools, code execution, file system access)
- When handling credentials, tokens, or sensitive data
- After Agente de Segurança/Compliance flags a concern

## Review Checklist

### 1. Prompt Injection
- [ ] Are user inputs sanitized before being inserted into prompts?
- [ ] Can an attacker craft a task description that overrides agent instructions?
- [ ] Are tool results from external sources treated as untrusted?

```python
# BAD - direct injection
prompt = f"Analyze this code: {user_input}"

# GOOD - structured separation
messages = [{"role": "user", "content": [{"type": "text", "text": user_input}]}]
```

### 2. Credential & Secret Handling
- [ ] No hardcoded API keys, tokens, or passwords
- [ ] All secrets loaded from environment variables or secret manager
- [ ] No secrets logged (check logging calls)
- [ ] `.env` files in `.gitignore`

```bash
# Scan for hardcoded secrets
grep -rE "(api_key|password|secret|token)\s*=\s*['\"][^'\"]{8,}" src/
```

### 3. Code Execution (Critical for Implementer Agent)
- [ ] Subprocess calls use list form (not shell=True)
- [ ] No `eval()` or `exec()` on untrusted input
- [ ] File paths validated before write operations
- [ ] Sandboxed execution environment for agent-generated code

```python
# BAD
subprocess.run(user_command, shell=True)

# GOOD
subprocess.run(["pytest", "tests/", "-x"], capture_output=True)
```

### 4. GitHub API Access (Principle of Least Privilege)
- [ ] Tokens have minimum required scopes
- [ ] Read-only tokens used where writes aren't needed
- [ ] No force-push permissions
- [ ] PR operations require human approval

### 5. SQL / NoSQL Injection (for task storage)
- [ ] All database queries use parameterized statements
- [ ] No string concatenation in queries

### 6. Data Exposure
- [ ] Task context (may contain code/secrets) encrypted at rest
- [ ] Telegram/web notifications don't leak sensitive code
- [ ] Log files don't contain secrets or full code diffs

### 7. Dependency Security
```bash
# Check for known vulnerabilities
pip-audit
# Or
safety check
```

## Severity Levels

- **CRITICAL** — Block merge immediately. Requires human security review.
  - Credential exposure, code injection, shell=True with untrusted input
- **HIGH** — Fix before merge.
  - Missing input validation, overly permissive tokens
- **MEDIUM** — Fix in same PR if quick, else file issue.
  - Excessive logging, non-parameterized queries
- **LOW** — File issue for next sprint.
  - Minor code quality security concerns

## AI-Specific Risks

| Risk | Description | Mitigation |
|------|-------------|------------|
| Prompt injection | Malicious task input hijacks agent behavior | Sanitize + structured prompts |
| Tool abuse | Agent calls destructive tools autonomously | Approval gates for irreversible actions |
| Context leakage | Task context contains secrets passed to LLM | Scrub secrets before LLM calls |
| Runaway execution | Agent loops or exceeds resource limits | Token budgets + execution timeouts |
