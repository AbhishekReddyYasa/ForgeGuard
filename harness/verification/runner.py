import subprocess
import sys
import time
from pathlib import Path

from harness.verification.result import VerificationResult


class VerificationRunner:
    """Execute predefined verification profiles inside an assigned workspace."""

    PROFILES = {
        "python_tests": ("-m", "pytest", "-q"),
        "ruff_lint": ("-m", "ruff", "check", "."),
        "ruff_format_check": ("-m", "ruff", "format", "--check", "."),
    }

    def __init__(
        self,
        workspace: Path,
        timeout_seconds: int = 60,
    ) -> None:
        self.workspace = Path(workspace).resolve()
        self.timeout_seconds = timeout_seconds

        if not self.workspace.exists() or not self.workspace.is_dir():
            raise ValueError("Workspace must be an existing directory.")

        if timeout_seconds <= 0:
            raise ValueError("Timeout must be greater than zero.")

    def run(self, check_name: str) -> VerificationResult:
        """Run one predefined verification profile."""

        if check_name not in self.PROFILES:
            raise ValueError(f"Check '{check_name}' is not registered.")

        command = [sys.executable, *self.PROFILES[check_name]]
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

            output_parts.append(f"Verification timed out after {self.timeout_seconds} seconds.")

            return VerificationResult(
                check_name=check_name,
                passed=False,
                duration_seconds=time.perf_counter() - start_time,
                output="\n".join(output_parts),
            )
