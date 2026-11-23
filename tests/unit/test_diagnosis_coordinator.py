import json

from agent.core.diagnosis_coordinator import DiagnosisCoordinator


def test_coordinator_diagnoses_failed_executions(tmp_path):
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
            "output": "FAILED test_calculator.py\nAssertionError",
        },
        {
            "check_name": "ruff_format_check",
            "passed": False,
            "duration_seconds": 0.8,
            "output": "1 file would be reformatted",
        },
    ]

    with log_file.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record) + "\n")

    coordinator = DiagnosisCoordinator(log_file)

    reports = coordinator.diagnose_failures()

    assert len(reports) == 2

    assert reports[0]["check_name"] == "python_tests"
    assert reports[0]["diagnosis"]["category"] == "test_failure"

    assert reports[1]["check_name"] == "ruff_format_check"
    assert reports[1]["diagnosis"]["category"] == "format_failure"


def test_coordinator_ignores_successful_executions(tmp_path):
    log_file = tmp_path / "execution_log.jsonl"

    record = {
        "check_name": "ruff_lint",
        "passed": True,
        "duration_seconds": 0.5,
        "output": "All checks passed!",
    }

    log_file.write_text(json.dumps(record) + "\n", encoding="utf-8")

    coordinator = DiagnosisCoordinator(log_file)

    reports = coordinator.diagnose_failures()

    assert reports == []


def test_coordinator_handles_missing_log_file(tmp_path):
    log_file = tmp_path / "missing_log.jsonl"

    coordinator = DiagnosisCoordinator(log_file)

    reports = coordinator.diagnose_failures()

    assert reports == []


def test_coordinator_summarises_multiple_failure_categories(tmp_path):
    log_file = tmp_path / "execution_log.jsonl"

    records = [
        {
            "check_name": "python_tests",
            "passed": False,
            "duration_seconds": 1.2,
            "output": "FAILED test_calculator.py\nE501 Line too long",
        },
        {
            "check_name": "ruff_format_check",
            "passed": False,
            "duration_seconds": 0.8,
            "output": "1 file would be reformatted",
        },
        {
            "check_name": "ruff_lint",
            "passed": True,
            "duration_seconds": 0.5,
            "output": "All checks passed!",
        },
    ]

    with log_file.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record) + "\n")

    coordinator = DiagnosisCoordinator(log_file)

    summary = coordinator.get_diagnosis_summary()

    assert summary["total_failed_executions"] == 2
    assert summary["total_detected_issues"] == 3

    assert summary["category_counts"] == {
        "test_failure": 1,
        "lint_failure": 1,
        "format_failure": 1,
    }


def test_coordinator_returns_zero_summary_without_failures(tmp_path):
    log_file = tmp_path / "execution_log.jsonl"

    record = {
        "check_name": "ruff_lint",
        "passed": True,
        "duration_seconds": 0.5,
        "output": "All checks passed!",
    }

    log_file.write_text(json.dumps(record) + "\n", encoding="utf-8")

    coordinator = DiagnosisCoordinator(log_file)

    summary = coordinator.get_diagnosis_summary()

    assert summary["total_failed_executions"] == 0
    assert summary["total_detected_issues"] == 0
    assert summary["category_counts"] == {}
