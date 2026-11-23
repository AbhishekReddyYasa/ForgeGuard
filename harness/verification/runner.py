
import subprocess
import time
from pathlib import Path

from harness.verification.result import VerificationResult


class VerificationRunner:
    """Execute registered verification checks inside an assigned workspace."""

    def __init__(
        self,
        workspace: Path,
        checks: dict[str, list[str]],
        timeout_seconds: int = 60,
    ) -> None:
        self.workspace = Path(workspace).resolve()
        self.checks = checks
        self.timeout_seconds = timeout_seconds

        if not self.workspace.exists() or not self.workspace.is_dir():
            raise ValueError("Workspace must be an existing directory.")

        if timeout_seconds <= 0:
            raise ValueError("Timeout must be greater than zero.")

        for name, command in checks.items():
            if not name.strip():
                raise ValueError("Check name cannot be empty.")

            if (
                not isinstance(command, list)
                or not command
                or any(not isinstance(arg, str) or not arg for arg in command)
            ):
                raise ValueError(f"Invalid command registered for check: {name}")

    def run(self, check_name: str) -> VerificationResult:
        """Run one registered check and return its verification result."""

        if check_name not in self.checks:
            raise ValueError(f"Check '{check_name}' is not registered.")

        command = self.checks[check_name]
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

            output = "\n".join(
                part for part in (completed.stdout, completed.stderr) if part
            )

            return VerificationResult(
                check_name=check_name,
                passed=completed.returncode == 0,
                duration_seconds=time.perf_counter() - start_time,
                output=output,
            )

        except subprocess.TimeoutExpired as error:
            output_parts = [
                part.decode(errors="replace") if isinstance(part, bytes) else part
                for part in (error.stdout, error.stderr)
                if part
            ]
            output_parts.append(
                f"Verification timed out after {self.timeout_seconds} seconds."
            )

            return VerificationResult(
                check_name=check_name,
                passed=False,
                duration_seconds=time.perf_counter() - start_time,
                output="\n".join(output_parts),
            )
