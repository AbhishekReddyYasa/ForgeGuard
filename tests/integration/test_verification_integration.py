
import sys
from pathlib import Path

from harness.verification.runner import VerificationRunner


def test_runner_executes_real_python_command(tmp_path):
    runner = VerificationRunner(
        workspace=Path(tmp_path),
        checks={
            "python_check": [
                sys.executable,
                "-c",
                "print('ForgeGuard execution successful')",
            ]
        },
    )

    result = runner.run("python_check")

    assert result.passed is True
    assert "ForgeGuard execution successful" in result.output


def test_runner_executes_real_failing_command(tmp_path):
    runner = VerificationRunner(
        workspace=Path(tmp_path),
        checks={
            "python_failure": [
                sys.executable,
                "-c",
                "raise SystemExit(1)",
            ]
        },
    )

    result = runner.run("python_failure")

    assert result.passed is False
