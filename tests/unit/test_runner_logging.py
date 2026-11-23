import json
from unittest.mock import Mock, patch

from harness.verification.runner import VerificationRunner


def test_runner_automatically_logs_successful_execution(tmp_path):
    runner = VerificationRunner(workspace=tmp_path)

    completed = Mock(
        returncode=0,
        stdout="All checks passed!",
        stderr="",
    )

    with patch(
        "harness.verification.runner.subprocess.run",
        return_value=completed,
    ):
        result = runner.run("ruff_lint")

    log_file = tmp_path / "reports" / "execution_log.jsonl"

    records = [json.loads(line) for line in log_file.read_text(encoding="utf-8").splitlines()]

    assert result.passed is True
    assert len(records) == 1
    assert records[0]["check_name"] == "ruff_lint"
    assert records[0]["passed"] is True
    assert records[0]["output"] == "All checks passed!"


def test_runner_automatically_logs_failed_execution(tmp_path):
    runner = VerificationRunner(workspace=tmp_path)

    completed = Mock(
        returncode=1,
        stdout="",
        stderr="Lint errors found",
    )

    with patch(
        "harness.verification.runner.subprocess.run",
        return_value=completed,
    ):
        result = runner.run("ruff_lint")

    log_file = tmp_path / "reports" / "execution_log.jsonl"

    records = [json.loads(line) for line in log_file.read_text(encoding="utf-8").splitlines()]

    assert result.passed is False
    assert len(records) == 1
    assert records[0]["passed"] is False
    assert records[0]["output"] == "Lint errors found"
