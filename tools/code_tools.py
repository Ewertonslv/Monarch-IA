import subprocess
import logging
from typing import Any

logger = logging.getLogger(__name__)


class CodeTools:
    """Run static analysis and test tools inside a working directory."""

    def __init__(self, workdir: str = ".") -> None:
        self.workdir = workdir

    def _run(self, cmd: list[str]) -> subprocess.CompletedProcess:
        return subprocess.run(
            cmd,
            cwd=self.workdir,
            capture_output=True,
            text=True,
        )

    # ------------------------------------------------------------------
    # Individual tools
    # ------------------------------------------------------------------

    def run_pytest(self, path: str = ".") -> dict[str, Any]:
        """Run pytest and return pass/fail + output."""
        proc = self._run(["python", "-m", "pytest", path, "-v", "--tb=short"])
        return {
            "passed": proc.returncode == 0,
            "output": proc.stdout + proc.stderr,
            "returncode": proc.returncode,
        }

    def run_ruff(self, path: str = ".") -> dict[str, Any]:
        """Run ruff linter and return issues list."""
        proc = self._run(["python", "-m", "ruff", "check", path])
        issues = [line for line in proc.stdout.splitlines() if line.strip()]
        return {
            "passed": proc.returncode == 0,
            "issues": issues,
            "output": proc.stdout,
        }

    def run_mypy(self, path: str = ".") -> dict[str, Any]:
        """Run mypy type checker."""
        proc = self._run(["python", "-m", "mypy", path, "--ignore-missing-imports"])
        return {
            "passed": proc.returncode == 0,
            "output": proc.stdout + proc.stderr,
        }

    def run_bandit(self, path: str = ".") -> dict[str, Any]:
        """Run bandit security scanner."""
        proc = self._run(["python", "-m", "bandit", "-r", path, "-f", "text"])
        combined = proc.stdout + proc.stderr
        high_count = combined.upper().count("SEVERITY: HIGH")
        return {
            "passed": proc.returncode == 0 and high_count == 0,
            "high_severity": high_count,
            "output": combined,
        }

    # ------------------------------------------------------------------
    # Aggregate
    # ------------------------------------------------------------------

    def run_all_checks(self, path: str = ".") -> dict[str, Any]:
        """Run pytest + ruff + mypy + bandit and return a combined summary."""
        pytest_res = self.run_pytest(path)
        ruff_res = self.run_ruff(path)
        mypy_res = self.run_mypy(path)
        bandit_res = self.run_bandit(path)

        overall = all(
            r["passed"]
            for r in [pytest_res, ruff_res, mypy_res, bandit_res]
        )

        return {
            "overall_passed": overall,
            "pytest": pytest_res,
            "ruff": ruff_res,
            "mypy": mypy_res,
            "bandit": bandit_res,
        }
