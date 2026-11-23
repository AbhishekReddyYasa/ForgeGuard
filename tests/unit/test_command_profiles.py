from unittest.mock import Mock, patch

import pytest
from harness.verification.runner import VerificationRunner


def test_runner_accepts_registered_profile(tmp_path):
    runner = VerificationRunner(workspace=tmp_path)

    completed = Mock(
        returncode=0,
        stdout="All checks passed",
        stderr="",
    )

    with patch(
        "harness.verification.runner.subprocess.run",
        return_value=completed,
    ) as mocked_run:
        result = runner.run("ruff_lint")

    assert result.passed is True
    assert result.check_name == "ruff_lint"

    command = mocked_run.call_args.args[0]

    assert command[1:3] == ["-m", "ruff"]
    assert command[3:] == ["check", "."]


def test_runner_rejects_unknown_profile(tmp_path):
    runner = VerificationRunner(workspace=tmp_path)

    with pytest.raises(ValueError, match="not registered"):
        runner.run("unknown_profile")


def test_runner_uses_current_python_interpreter(tmp_path):
    import sys

    runner = VerificationRunner(workspace=tmp_path)

    completed = Mock(
        returncode=0,
        stdout="",
        stderr="",
    )

    with patch(
        "harness.verification.runner.subprocess.run",
        return_value=completed,
    ) as mocked_run:
        runner.run("ruff_lint")

    command = mocked_run.call_args.args[0]

    assert command[0] == sys.executable
