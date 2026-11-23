from unittest.mock import Mock, patch

import pytest
from harness.verification.runner import VerificationRunner


def test_runner_records_successful_check(tmp_path):
    runner = VerificationRunner(
        workspace=tmp_path,
        checks={"python_tests": ["python", "-m", "pytest"]},
    )

    completed = Mock(
        returncode=0,
        stdout="5 tests passed",
        stderr="",
    )

    with patch("harness.verification.runner.subprocess.run", return_value=completed):
        result = runner.run("python_tests")

    assert result.check_name == "python_tests"
    assert result.passed is True
    assert result.output == "5 tests passed"
    assert result.duration_seconds >= 0


def test_runner_records_failed_check(tmp_path):
    runner = VerificationRunner(
        workspace=tmp_path,
        checks={"ruff": ["ruff", "check", "."]},
    )

    completed = Mock(
        returncode=1,
        stdout="",
        stderr="Found 2 errors",
    )

    with patch("harness.verification.runner.subprocess.run", return_value=completed):
        result = runner.run("ruff")

    assert result.passed is False
    assert result.output == "Found 2 errors"


def test_runner_rejects_unregistered_check(tmp_path):
    runner = VerificationRunner(
        workspace=tmp_path,
        checks={"python_tests": ["python", "-m", "pytest"]},
    )

    with pytest.raises(ValueError, match="not registered"):
        runner.run("unknown_check")


def test_runner_handles_timeout(tmp_path):
    runner = VerificationRunner(
        workspace=tmp_path,
        checks={"slow_check": ["python", "slow_script.py"]},
        timeout_seconds=5,
    )

    with patch(
        "harness.verification.runner.subprocess.run",
        side_effect=__import__("subprocess").TimeoutExpired(
            cmd=["python", "slow_script.py"],
            timeout=5,
        ),
    ):
        result = runner.run("slow_check")

    assert result.passed is False
    assert "timed out" in result.output.lower()

def test_runner_rejects_unapproved_executable(tmp_path):
    runner = VerificationRunner(
        workspace=tmp_path,
        checks={"unsafe": ["cmd.exe", "/c", "echo unsafe"]},
    )

    with pytest.raises(ValueError, match="not allowed"):
        runner.run("unsafe")


def test_runner_rejects_empty_command_arguments(tmp_path):
    with pytest.raises(ValueError, match="Invalid command"):
        VerificationRunner(
            workspace=tmp_path,
            checks={"invalid": ["python", ""]},
        )
