import json

from harness.observability.execution_logger import ExecutionLogger


def test_logger_records_successful_execution(tmp_path):
    log_file = tmp_path / "execution_log.jsonl"
    logger = ExecutionLogger(log_file)

    logger.record(
        check_name="ruff_lint",
        passed=True,
        duration_seconds=1.25,
        output="All checks passed!",
    )

    records = [json.loads(line) for line in log_file.read_text(encoding="utf-8").splitlines()]

    assert len(records) == 1
    assert records[0]["check_name"] == "ruff_lint"
    assert records[0]["passed"] is True
    assert records[0]["duration_seconds"] == 1.25
    assert records[0]["output"] == "All checks passed!"
    assert "timestamp" in records[0]


def test_logger_preserves_previous_records(tmp_path):
    log_file = tmp_path / "execution_log.jsonl"
    logger = ExecutionLogger(log_file)

    logger.record("python_tests", True, 2.0, "Tests passed")
    logger.record("ruff_lint", False, 1.0, "Lint failed")

    records = [json.loads(line) for line in log_file.read_text(encoding="utf-8").splitlines()]

    assert len(records) == 2
    assert records[0]["check_name"] == "python_tests"
    assert records[1]["check_name"] == "ruff_lint"
    assert records[1]["passed"] is False
