import pytest
from harness.verification.result import VerificationResult


def test_verification_result_records_success():
    result = VerificationResult(
        check_name="Python Tests",
        passed=True,
        duration_seconds=2.41,
        output="5 tests passed",
    )

    assert result.check_name == "Python Tests"
    assert result.passed is True
    assert result.duration_seconds == 2.41
    assert result.output == "5 tests passed"


def test_verification_result_records_failure():
    result = VerificationResult(
        check_name="Ruff Lint",
        passed=False,
        duration_seconds=1.25,
        output="Found 2 errors",
    )

    assert result.passed is False
    assert result.check_name == "Ruff Lint"


def test_empty_check_name_is_rejected():
    with pytest.raises(ValueError, match="Check name cannot be empty"):
        VerificationResult(
            check_name="",
            passed=True,
            duration_seconds=1.0,
            output="",
        )


def test_negative_duration_is_rejected():
    with pytest.raises(ValueError, match="Duration cannot be negative"):
        VerificationResult(
            check_name="Python Tests",
            passed=True,
            duration_seconds=-1.0,
            output="",
        )
