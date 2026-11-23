import json
from pathlib import Path
from typing import Any


class ExecutionHistory:
    """Read, filter, and summarize verification execution history."""

    def __init__(self, log_file: Path) -> None:
        self.log_file = Path(log_file)

    def load(self) -> list[dict[str, Any]]:
        """Load all execution records from the JSONL log."""

        if not self.log_file.exists():
            return []

        records = []

        with self.log_file.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                if not line.strip():
                    continue

                try:
                    record = json.loads(line)
                except json.JSONDecodeError as error:
                    raise ValueError(f"Invalid JSON on line {line_number}: {error}") from error

                if not isinstance(record, dict):
                    raise ValueError(
                        f"Invalid record on line {line_number}: Expected a JSON object."
                    )

                records.append(record)

        return records

    def filter_records(
        self,
        check_name: str | None = None,
        passed: bool | None = None,
    ) -> list[dict[str, Any]]:
        """Filter execution records by check name and pass/fail status."""

        records = self.load()

        if check_name is not None:
            records = [record for record in records if record.get("check_name") == check_name]

        if passed is not None:
            records = [record for record in records if record.get("passed") is passed]

        return records

    def get_statistics(self) -> dict[str, int | float]:
        """Calculate overall execution statistics."""

        records = self.load()

        total = len(records)
        successful = sum(record.get("passed") is True for record in records)
        failed = sum(record.get("passed") is False for record in records)

        success_rate = (successful / total) * 100 if total > 0 else 0.0

        return {
            "total": total,
            "successful": successful,
            "failed": failed,
            "success_rate": round(success_rate, 2),
        }
