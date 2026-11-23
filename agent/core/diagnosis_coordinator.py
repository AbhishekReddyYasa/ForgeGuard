from collections import Counter
from pathlib import Path
from typing import Any

from agent.core.failure_diagnoser import FailureDiagnoser
from harness.observability.execution_history import ExecutionHistory


class DiagnosisCoordinator:
    """Coordinate execution history retrieval and failure diagnosis."""

    def __init__(self, log_file: Path) -> None:
        self.history = ExecutionHistory(log_file)
        self.diagnoser = FailureDiagnoser()

    def diagnose_failures(self) -> list[dict[str, Any]]:
        """Find failed executions and diagnose their recorded output."""

        failed_records = self.history.filter_records(passed=False)
        reports = []

        for record in failed_records:
            diagnosis = self.diagnoser.diagnose(record.get("output", ""))

            reports.append(
                {
                    "check_name": record.get("check_name", "unknown"),
                    "timestamp": record.get("timestamp"),
                    "duration_seconds": record.get("duration_seconds"),
                    "diagnosis": diagnosis,
                }
            )

        return reports

    def get_diagnosis_summary(self) -> dict[str, Any]:
        """Summarise the failure categories across all diagnosis reports."""

        reports = self.diagnose_failures()
        category_counts = Counter()

        for report in reports:
            for issue in report["diagnosis"]["detected_issues"]:
                category_counts[issue["category"]] += 1

        return {
            "total_failed_executions": len(reports),
            "total_detected_issues": sum(category_counts.values()),
            "category_counts": dict(category_counts),
        }
