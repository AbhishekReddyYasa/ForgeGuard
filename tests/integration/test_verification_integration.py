from pathlib import Path

from harness.verification.runner import VerificationRunner


def test_runner_executes_real_python_tests(tmp_path):
    test_file = tmp_path / "test_sample.py"

    test_file.write_text(
        "def test_sample():\n    assert 2 + 2 == 4\n",
        encoding="utf-8",
    )

    runner = VerificationRunner(
        workspace=Path(tmp_path),
        timeout_seconds=30,
    )

    result = runner.run("python_tests")

    assert result.passed is True
    assert "1 passed" in result.output


def test_runner_executes_real_ruff_lint():
    workspace = Path(__file__).resolve().parents[2]

    runner = VerificationRunner(
        workspace=workspace,
        timeout_seconds=60,
    )

    result = runner.run("ruff_lint")

    assert result.passed is True
    assert "all checks passed" in result.output.lower()


def test_runner_executes_real_ruff_format_check():
    workspace = Path(__file__).resolve().parents[2]

    runner = VerificationRunner(
        workspace=workspace,
        timeout_seconds=60,
    )

    result = runner.run("ruff_format_check")

    assert result.passed is True
