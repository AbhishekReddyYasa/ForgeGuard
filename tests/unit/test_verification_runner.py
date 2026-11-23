import subprocess
from unittest.mock import Mock, patch

import pytest
from harness.verification.runner import VerificationRunner


def test_runner_records_successful_check(tmp_path):
    runner = VerificationRunner(workspace=tmp_path)

    completed = Mock(
        returncode=0,
        stdout="All checks passed",
        stderr="",
    )

    with patch(
        "harness.verification.runner.subprocess.run",
        return_value=completed,
    ):
        result = runner.run("ruff_lint")

    assert result.check_name == "ruff_lint"
    assert result.passed is True
    assert result.output == "All checks passed"
    assert result.duration_seconds >= 0


def test_runner_records_failed_check(tmp_path):
    runner = VerificationRunner(workspace=tmp_path)

    completed = Mock(
        returncode=1,
        stdout="",
        stderr="Found 2 errors",
    )

    with patch(
        "harness.verification.runner.subprocess.run",
        return_value=completed,
    ):
        result = runner.run("ruff_lint")

    assert result.passed is False
    assert result.output == "Found 2 errors"


def test_runner_rejects_unregistered_profile(tmp_path):
    runner = VerificationRunner(workspace=tmp_path)

    with pytest.raises(ValueError, match="not registered"):
        runner.run("unknown_profile")


def test_runner_handles_timeout(tmp_path):
    runner = VerificationRunner(
        workspace=tmp_path,
        timeout_seconds=5,
    )

    with patch(
        "harness.verification.runner.subprocess.run",
        side_effect=subprocess.TimeoutExpired(
            cmd=["python", "-m", "ruff"],
            timeout=5,
        ),
    ):
        result = runner.run("ruff_lint")

    assert result.passed is False
    assert "timed out" in result.output.lower()


def test_runner_rejects_invalid_workspace(tmp_path):
    missing_workspace = tmp_path / "missing"

    with pytest.raises(ValueError, match="existing directory"):
        VerificationRunner(workspace=missing_workspace)


def test_runner_rejects_nonpositive_timeout(tmp_path):
    with pytest.raises(ValueError, match="greater than zero"):
        VerificationRunner(
            workspace=tmp_path,
            timeout_seconds=0,
        )
