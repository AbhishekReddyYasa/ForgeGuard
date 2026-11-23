import subprocess
import time
from pathlib import Path
from typing import Any

from harness.observability.execution_logger import ExecutionLogger
from harness.security.action_registry import ActionRegistry


class ControlledExecutor:
    """Execute predefined actions and record their outcomes."""

    def __init__(
        self,
        workspace: Path,
        timeout_seconds: int = 60,
        logger: ExecutionLogger | None = None,
    ) -> None:
        self.workspace = Path(workspace).resolve()
        self.timeout_seconds = timeout_seconds
        self.registry = ActionRegistry()

        if not self.workspace.is_dir():
            raise ValueError("Workspace must be an existing directory.")

        if timeout_seconds <= 0:
            raise ValueError("Timeout must be greater than zero.")

        self.logger = logger or ExecutionLogger(self.workspace / "reports" / "execution_log.jsonl")

    def _validate_target(self, target: str | Path) -> Path:
        """Validate a Python target and reject symlinks and path traversal."""

        candidate = Path(target)

        if ".." in candidate.parts:
            raise ValueError("Parent-directory traversal is not permitted.")

        if not candidate.is_absolute():
            candidate = self.workspace / candidate

        try:
            relative = candidate.relative_to(self.workspace)
        except ValueError as error:
            raise ValueError("Target must remain inside the workspace.") from error

        current = self.workspace

        for part in relative.parts:
            current = current / part

            if current.is_symlink():
                raise ValueError("Symbolic links are not permitted.")

        resolved = candidate.resolve()

        try:
            resolved.relative_to(self.workspace)
        except ValueError as error:
            raise ValueError("Target must remain inside the workspace.") from error

        if resolved.suffix.lower() != ".py":
            raise ValueError("Only Python files can be formatted.")

        if not resolved.is_file():
            raise ValueError("Target must be an existing file.")

        return resolved

    def _record_result(
        self,
        action_id: str,
        passed: bool,
        return_code: int | None,
        duration_seconds: float,
        output: str,
    ) -> dict[str, Any]:
        """Record an execution outcome and return its result."""

        self.logger.record(
            check_name=action_id,
            passed=passed,
            duration_seconds=duration_seconds,
            output=output,
        )

        return {
            "action_id": action_id,
            "passed": passed,
            "return_code": return_code,
            "duration_seconds": duration_seconds,
            "output": output,
        }

    def execute(
        self,
        action_id: str,
        approved: bool = False,
        target: str | Path | None = None,
    ) -> dict[str, Any]:
        """Execute a registered action after applying safety checks."""

        action = self.registry.get_action(action_id)

        if action.requires_approval and approved is not True:
            raise PermissionError("Human approval is required for this action.")

        validated_target = None

        if action.modifies_files:
            if target is None:
                raise ValueError("A target file is required.")

            validated_target = self._validate_target(target)

        elif target is not None:
            raise ValueError("This action does not accept a target file.")

        command = self.registry.build_command(
            action_id,
            validated_target,
        )

        start_time = time.perf_counter()

        try:
            completed = subprocess.run(
                command,
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=False,
                shell=False,
            )

            output = "\n".join(part for part in (completed.stdout, completed.stderr) if part)

            return self._record_result(
                action_id=action_id,
                passed=completed.returncode == 0,
                return_code=completed.returncode,
                duration_seconds=time.perf_counter() - start_time,
                output=output,
            )

        except subprocess.TimeoutExpired as error:
            output_parts = [
                part.decode(errors="replace") if isinstance(part, bytes) else part
                for part in (error.stdout, error.stderr)
                if part
            ]

            output_parts.append(f"Execution timed out after {self.timeout_seconds} seconds.")

            return self._record_result(
                action_id=action_id,
                passed=False,
                return_code=None,
                duration_seconds=time.perf_counter() - start_time,
                output="\n".join(output_parts),
            )
