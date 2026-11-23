import json

import pytest
from harness.observability.execution_history import ExecutionHistory


def test_history_loads_multiple_records(tmp_path):
    log_file = tmp_path / "execution_log.jsonl"

    records = [
        {
            "check_name": "ruff_lint",
            "passed": True,
            "duration_seconds": 0.5,
            "output": "All checks passed!",
        },
        {
            "check_name": "python_tests",
            "passed": False,
            "duration_seconds": 1.2,
            "output": "Tests failed.",
        },
    ]

    with log_file.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record) + "\n")

    history = ExecutionHistory(log_file)

    assert history.load() == records


def test_history_returns_empty_list_when_file_missing(tmp_path):
    log_file = tmp_path / "missing_log.jsonl"

    history = ExecutionHistory(log_file)

    assert history.load() == []


def test_history_rejects_malformed_json(tmp_path):
    log_file = tmp_path / "execution_log.jsonl"
    log_file.write_text('{"check_name": "ruff_lint"\n', encoding="utf-8")

    history = ExecutionHistory(log_file)

    with pytest.raises(ValueError, match="line 1"):
        history.load()


def test_history_rejects_non_object_records(tmp_path):
    log_file = tmp_path / "execution_log.jsonl"
    log_file.write_text('["invalid record"]\n', encoding="utf-8")

    history = ExecutionHistory(log_file)

    with pytest.raises(ValueError, match="Expected a JSON object"):
        history.load()


def test_history_filters_records_by_check_name(tmp_path):
    log_file = tmp_path / "execution_log.jsonl"

    records = [
        {"check_name": "ruff_lint", "passed": True},
        {"check_name": "python_tests", "passed": False},
        {"check_name": "ruff_lint", "passed": False},
    ]

    with log_file.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record) + "\n")

    history = ExecutionHistory(log_file)

    filtered = history.filter_records(check_name="ruff_lint")

    assert len(filtered) == 2
    assert all(record["check_name"] == "ruff_lint" for record in filtered)


def test_history_filters_records_by_status(tmp_path):
    log_file = tmp_path / "execution_log.jsonl"

    records = [
        {"check_name": "ruff_lint", "passed": True},
        {"check_name": "python_tests", "passed": False},
        {"check_name": "ruff_format_check", "passed": True},
    ]

    with log_file.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record) + "\n")

    history = ExecutionHistory(log_file)

    failed_records = history.filter_records(passed=False)

    assert len(failed_records) == 1
    assert failed_records[0]["check_name"] == "python_tests"


def test_history_filters_by_name_and_status(tmp_path):
    log_file = tmp_path / "execution_log.jsonl"

    records = [
        {"check_name": "ruff_lint", "passed": True},
        {"check_name": "ruff_lint", "passed": False},
        {"check_name": "python_tests", "passed": False},
    ]

    with log_file.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record) + "\n")

    history = ExecutionHistory(log_file)

    filtered = history.filter_records(
        check_name="ruff_lint",
        passed=False,
    )

    assert len(filtered) == 1
    assert filtered[0]["check_name"] == "ruff_lint"
    assert filtered[0]["passed"] is False


def test_history_calculates_statistics(tmp_path):
    log_file = tmp_path / "execution_log.jsonl"

    records = [
        {"check_name": "ruff_lint", "passed": True},
        {"check_name": "python_tests", "passed": True},
        {"check_name": "ruff_format_check", "passed": False},
        {"check_name": "ruff_lint", "passed": True},
    ]

    with log_file.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record) + "\n")

    history = ExecutionHistory(log_file)

    statistics = history.get_statistics()

    assert statistics["total"] == 4
    assert statistics["successful"] == 3
    assert statistics["failed"] == 1
    assert statistics["success_rate"] == 75.0


def test_history_returns_zero_statistics_when_file_missing(tmp_path):
    log_file = tmp_path / "missing_log.jsonl"

    history = ExecutionHistory(log_file)

    statistics = history.get_statistics()

    assert statistics["total"] == 0
    assert statistics["successful"] == 0
    assert statistics["failed"] == 0
    assert statistics["success_rate"] == 0.0
