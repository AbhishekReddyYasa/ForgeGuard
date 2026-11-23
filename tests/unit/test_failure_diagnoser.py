from agent.core.failure_diagnoser import FailureDiagnoser


def test_diagnoses_test_failure():
    diagnoser = FailureDiagnoser()

    result = diagnoser.diagnose("FAILED tests/test_calculator.py::test_addition\nAssertionError")

    assert result["category"] == "test_failure"


def test_diagnoses_lint_failure():
    diagnoser = FailureDiagnoser()

    result = diagnoser.diagnose("F401 imported but unused")

    assert result["category"] == "lint_failure"


def test_diagnoses_format_failure():
    diagnoser = FailureDiagnoser()

    result = diagnoser.diagnose("1 file would be reformatted")

    assert result["category"] == "format_failure"


def test_diagnoses_timeout():
    diagnoser = FailureDiagnoser()

    result = diagnoser.diagnose("Verification timed out after 60 seconds.")

    assert result["category"] == "timeout"


def test_diagnoses_execution_error():
    diagnoser = FailureDiagnoser()

    result = diagnoser.diagnose("ModuleNotFoundError: No module named 'pytest'")

    assert result["category"] == "execution_error"


def test_diagnoses_unknown_failure():
    diagnoser = FailureDiagnoser()

    result = diagnoser.diagnose("Unexpected system failure.")

    assert result["category"] == "unknown_failure"


def test_handles_empty_output():
    diagnoser = FailureDiagnoser()

    result = diagnoser.diagnose("")

    assert result["category"] == "unknown_failure"
    assert result["description"] == "No error output was provided."


def test_diagnoses_first_matching_failure_when_multiple_patterns_exist():
    diagnoser = FailureDiagnoser()

    result = diagnoser.diagnose("FAILED tests/test_runner.py\nE501 Line too long")

    assert result["category"] == "test_failure"


def test_diagnoses_multiple_failure_categories():
    diagnoser = FailureDiagnoser()

    result = diagnoser.diagnose(
        "FAILED tests/test_runner.py\n"
        "AssertionError: expected 5 but got 4\n"
        "E501 Line too long (105 > 100)"
    )

    categories = [issue["category"] for issue in result["detected_issues"]]

    assert result["category"] == "test_failure"
    assert "test_failure" in categories
    assert "lint_failure" in categories
    assert len(categories) == 2


def test_detected_issues_contain_descriptions_and_suggestions():
    diagnoser = FailureDiagnoser()

    result = diagnoser.diagnose("F401 imported but unused")

    issue = result["detected_issues"][0]

    assert issue["category"] == "lint_failure"
    assert issue["description"]
    assert issue["suggestion"]


def test_unknown_failure_has_no_detected_issues():
    diagnoser = FailureDiagnoser()

    result = diagnoser.diagnose("Unexpected database connection problem.")

    assert result["category"] == "unknown_failure"
    assert result["detected_issues"] == []
