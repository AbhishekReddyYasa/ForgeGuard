import json
from datetime import UTC, datetime
from pathlib import Path


class ExecutionLogger:
    """Record verification executions in JSON Lines format."""

    def __init__(self, log_file: Path) -> None:
        self.log_file = Path(log_file)

        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def record(
        self,
        check_name: str,
        passed: bool,
        duration_seconds: float,
        output: str,
    ) -> None:
        """Append one verification execution record to the log."""

        if not check_name.strip():
            raise ValueError("Check name cannot be empty.")

        if duration_seconds < 0:
            raise ValueError("Duration cannot be negative.")

        record = {
            "timestamp": datetime.now(UTC).isoformat(),
            "check_name": check_name,
            "passed": passed,
            "duration_seconds": duration_seconds,
            "output": output,
        }

        with self.log_file.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record) + "\n")
