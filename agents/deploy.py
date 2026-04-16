import json
import logging
from typing import Any

from agents.base import BaseAgent, SONNET_MODEL
from core.task import Task
from tools.github_tools import GitHubTools

logger = logging.getLogger(__name__)

_SYSTEM = """You are the Deploy Agent for Monarch AI.

You analyse the project structure and generate CI/CD configuration so the code is
automatically tested on every push and ready to be deployed.

Your responsibilities:
1. Detect the project type (FastAPI, CLI, bot, library, etc.)
2. Generate a GitHub Actions CI workflow that runs tests, linting, and type checking
3. Recommend a deployment target based on the project type
4. List any environment variables the deployed app will need

Always write a `.github/workflows/ci.yml` to the feature branch.

Respond with a single JSON object:
{
  "confidence": <float 0-1>,
  "project_type": <str>,            // fastapi_api | telegram_bot | cli_tool | library | fullstack | other
  "deployment_target": <str>,       // railway | render | vercel | vps | none
  "ci_workflow_path": <str>,        // always ".github/workflows/ci.yml"
  "ci_workflow_content": <str>,     // full YAML content of the workflow
  "files_written": [<str>, ...],
  "env_vars_needed": [<str>, ...],  // env vars the running app needs (not secrets)
  "deploy_commands": [<str>, ...],  // commands to deploy manually if needed
  "concerns": [<str>, ...]
}"""

_CI_TEMPLATE = """\
name: CI

on:
  push:
    branches: ["**"]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.14"
          cache: pip

      - name: Install dependencies
        run: pip install -e ".[dev]"

      - name: Run tests
        run: python -m pytest -v

      - name: Lint (ruff)
        run: python -m ruff check .

      - name: Type check (mypy)
        run: python -m mypy . --ignore-missing-imports

      - name: Security scan (bandit)
        run: python -m bandit -r . -x tests/
"""


class DeployAgent(BaseAgent):
    name = "deploy"
    display_name = "Julia - Deploy"
    model = SONNET_MODEL
    system_prompt = _SYSTEM

    def __init__(self) -> None:
        super().__init__()
        self._github = GitHubTools()

    async def build_user_message(self, task: Task) -> str:
        arch = task.architecture or {}
        branch = task.branch_name or "main"

        # Try to read the file tree for context
        try:
            files = self._github.list_files(ref=branch)
        except Exception:
            files = []

        return (
            f"Analyse this project and generate CI/CD configuration.\n\n"
            f"Task: {task.raw_input}\n\n"
            f"Branch: {branch}\n\n"
            f"Architecture:\n{json.dumps(arch, indent=2)}\n\n"
            f"Existing files in repo:\n{json.dumps(files[:50], indent=2)}\n\n"
            f"Generate a GitHub Actions CI workflow and recommend a deployment target.\n"
            f"Include the full YAML content in 'ci_workflow_content'."
        )

    async def run(self, task: Task):
        result = await super().run(task)

        # Write the CI workflow file to the branch (if we have a branch)
        ci_content = result.output.get("ci_workflow_content", _CI_TEMPLATE)
        ci_path = result.output.get("ci_workflow_path", ".github/workflows/ci.yml")
        branch = task.branch_name

        if branch:
            try:
                self._github.write_file(
                    path=ci_path,
                    content=ci_content,
                    commit_message="ci: add GitHub Actions workflow",
                    branch=branch,
                )
                logger.info("[deploy] Wrote %s to branch %s", ci_path, branch)
            except Exception as exc:
                logger.warning("[deploy] Could not write CI workflow: %s", exc)

        task.deploy_report = result.output
        task.add_history(
            agent=self.label,
            action="deploy_config_complete",
            detail=(
                f"type={result.output.get('project_type')} "
                f"target={result.output.get('deployment_target')} "
                f"files={len(result.output.get('files_written', []))}"
            ),
        )
        return result
