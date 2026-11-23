import subprocess
import sys

import pytest
from harness.security.controlled_executor import ControlledExecutor


@pytest.fixture
def executor(tmp_path):
    return ControlledExecutor(tmp_path, timeout_seconds=10)


def test_rejects_invalid_workspace():
    with pytest.raises(ValueError):
        ControlledExecutor("missing_workspace")


def test_rejects_nonpositive_timeout(tmp_path):
    with pytest.raises(ValueError):
        ControlledExecutor(tmp_path, timeout_seconds=0)


def test_unapproved_formatting_is_blocked(executor, tmp_path):
    target = tmp_path / "example.py"
    target.write_text("x=1\n", encoding="utf-8")

    with pytest.raises(PermissionError):
        executor.execute("format_python_file", target=target)


def test_unknown_action_is_rejected(executor):
    with pytest.raises(ValueError):
        executor.execute("delete_everything")


def test_formatting_requires_existing_target(executor):
    with pytest.raises(ValueError):
        executor.execute(
            "format_python_file",
            approved=True,
            target="missing.py",
        )


def test_formatting_rejects_non_python_file(executor, tmp_path):
    target = tmp_path / "notes.txt"
    target.write_text("notes", encoding="utf-8")

    with pytest.raises(ValueError):
        executor.execute(
            "format_python_file",
            approved=True,
            target=target,
        )


def test_formatting_rejects_path_outside_workspace(executor, tmp_path):
    outside = tmp_path.parent / "outside.py"
    outside.write_text("x=1\n", encoding="utf-8")

    with pytest.raises(ValueError):
        executor.execute(
            "format_python_file",
            approved=True,
            target=outside,
        )


def test_formatting_rejects_parent_directory_traversal(executor):
    with pytest.raises(ValueError):
        executor.execute(
            "format_python_file",
            approved=True,
            target="../outside.py",
        )


def test_formatting_rejects_symlink(executor, tmp_path):
    target = tmp_path / "linked.py"
    original = tmp_path / "original.py"
    original.write_text("x=1\n", encoding="utf-8")

    try:
        target.symlink_to(original)
    except (OSError, NotImplementedError):
        pytest.skip("Symbolic links are unavailable on this system.")

    with pytest.raises(ValueError, match="Symbolic links"):
        executor.execute(
            "format_python_file",
            approved=True,
            target=target,
        )


def test_read_only_action_rejects_target(executor, tmp_path):
    target = tmp_path / "example.py"
    target.write_text("x=1\n", encoding="utf-8")

    with pytest.raises(ValueError):
        executor.execute("run_python_tests", target=target)


def test_executes_registered_read_only_action(executor, monkeypatch):
    def fake_run(command, **kwargs):
        assert command[0] == sys.executable
        assert command[1:] == ["-m", "ruff", "check", "."]
        assert kwargs["shell"] is False
        assert kwargs["cwd"] == executor.workspace

        return subprocess.CompletedProcess(command, 0, stdout="All checks passed!", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = executor.execute("run_ruff_lint")

    assert result["passed"] is True
    assert result["return_code"] == 0
    assert "All checks passed!" in result["output"]


def test_failed_command_returns_failure_result(executor, monkeypatch):
    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(command, 1, stdout="", stderr="Lint errors found")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = executor.execute("run_ruff_lint")

    assert result["passed"] is False
    assert result["return_code"] == 1
    assert "Lint errors found" in result["output"]


def test_timeout_returns_failure_result(executor, monkeypatch):
    def fake_run(command, **kwargs):
        raise subprocess.TimeoutExpired(command, timeout=10)

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = executor.execute("run_ruff_lint")

    assert result["passed"] is False
    assert result["return_code"] is None
    assert "timed out" in result["output"].lower()


def test_approved_formatting_executes_on_workspace_file(executor, tmp_path, monkeypatch):
    target = tmp_path / "example.py"
    target.write_text("x=1\n", encoding="utf-8")

    def fake_run(command, **kwargs):
        assert command[-1] == str(target)
        assert kwargs["shell"] is False

        return subprocess.CompletedProcess(command, 0, stdout="1 file reformatted", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = executor.execute(
        "format_python_file",
        approved=True,
        target=target,
    )

    assert result["passed"] is True
    assert result["action_id"] == "format_python_file"
