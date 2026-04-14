import pytest
from unittest.mock import patch, MagicMock
from tools.code_tools import CodeTools


@pytest.fixture
def ct():
    return CodeTools(workdir="/tmp/monarch_test")


def _make_proc(returncode: int, stdout: str, stderr: str = "") -> MagicMock:
    proc = MagicMock()
    proc.returncode = returncode
    proc.stdout = stdout
    proc.stderr = stderr
    return proc


def test_run_pytest_passes(ct):
    with patch("tools.code_tools.subprocess.run", return_value=_make_proc(0, "3 passed")) as mock_run:
        result = ct.run_pytest()
    assert result["passed"] is True
    assert "3 passed" in result["output"]


def test_run_pytest_fails(ct):
    with patch("tools.code_tools.subprocess.run", return_value=_make_proc(1, "1 failed\n2 passed")):
        result = ct.run_pytest()
    assert result["passed"] is False


def test_run_ruff_clean(ct):
    with patch("tools.code_tools.subprocess.run", return_value=_make_proc(0, "")):
        result = ct.run_ruff()
    assert result["passed"] is True
    assert result["issues"] == []


def test_run_ruff_has_issues(ct):
    output = "src/foo.py:10:1: E501 line too long"
    with patch("tools.code_tools.subprocess.run", return_value=_make_proc(1, output)):
        result = ct.run_ruff()
    assert result["passed"] is False
    assert len(result["issues"]) == 1


def test_run_mypy_passes(ct):
    with patch("tools.code_tools.subprocess.run", return_value=_make_proc(0, "Success: no issues found")):
        result = ct.run_mypy()
    assert result["passed"] is True


def test_run_bandit_clean(ct):
    with patch("tools.code_tools.subprocess.run", return_value=_make_proc(0, "No issues identified.")):
        result = ct.run_bandit()
    assert result["passed"] is True
    assert result["high_severity"] == 0


def test_run_bandit_high_severity(ct):
    output = "Issue: [B101:assert_used] Use of assert detected.\nSeverity: High"
    with patch("tools.code_tools.subprocess.run", return_value=_make_proc(1, output)):
        result = ct.run_bandit()
    assert result["passed"] is False
    assert result["high_severity"] >= 1


def test_run_all_checks(ct):
    good = _make_proc(0, "ok")
    with patch("tools.code_tools.subprocess.run", return_value=good):
        summary = ct.run_all_checks()
    assert "pytest" in summary
    assert "ruff" in summary
    assert "mypy" in summary
    assert "bandit" in summary
    assert summary["overall_passed"] is True
