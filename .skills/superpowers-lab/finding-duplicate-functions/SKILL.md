---
name: finding-duplicate-functions
description: "Detects semantic code duplication — functions with the same intent but different implementations. Use after implementing multiple agents or utilities to find consolidation opportunities."
---

# Finding Duplicate-Intent Functions

Identifies functions with identical purposes but different implementations — semantic duplicates that classical copy-paste detectors (jscpd) miss.

## Five-Phase Workflow

1. **Extract** — Build a function catalog from the codebase
2. **Categorize** — Deploy a Haiku subagent to group functions by domain
3. **Split** — Organize categorized functions into separate files for analysis
4. **Detect** — Run Opus subagents on each category to identify semantic duplicates
5. **Report** — Generate a prioritized markdown summary for human review

## Key Rules

- Use **Haiku** for categorization (speed), **Opus** for duplicate analysis (accuracy)
- Minimum 3 functions per category before analysis
- Exclude test files by default (test utilities are less likely consolidation candidates)
- Before consolidating: verify the surviving function has adequate test coverage

## High-Risk Areas

Validation code, error formatting, and path manipulation are particularly prone to duplication across utility-focused directories.

## When to Use for Monarch AI

- After implementing multiple agents (base classes, tool wrappers)
- After adding GitHub tools and code analysis tools
- Before any major refactor phase
