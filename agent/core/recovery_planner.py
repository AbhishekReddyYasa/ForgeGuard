from typing import Any


class RecoveryPlanner:
    """Generate predefined recovery proposals from failure diagnoses."""

    RECOVERY_ACTIONS = {
        "test_failure": {
            "action_id": "run_python_tests",
            "description": "Rerun the project's Python test suite.",
            "risk_level": "low",
            "requires_approval": False,
        },
        "lint_failure": {
            "action_id": "run_ruff_lint",
            "description": "Rerun Ruff lint checks on the project.",
            "risk_level": "low",
            "requires_approval": False,
        },
        "format_failure": {
            "action_id": "format_python_file",
            "description": "Format an approved Python file using Ruff.",
            "risk_level": "medium",
            "requires_approval": True,
        },
        "timeout": {
            "action_id": "manual_investigation",
            "description": "Inspect execution duration and timeout settings.",
            "risk_level": "low",
            "requires_approval": True,
        },
        "execution_error": {
            "action_id": "manual_investigation",
            "description": "Inspect dependencies and execution configuration.",
            "risk_level": "low",
            "requires_approval": True,
        },
        "unknown_failure": {
            "action_id": "manual_investigation",
            "description": "Request manual investigation of the failure.",
            "risk_level": "low",
            "requires_approval": True,
        },
    }

    def create_plan(self, diagnosis: dict[str, Any]) -> dict[str, Any]:
        """Create a recovery proposal from a failure diagnosis."""

        if not isinstance(diagnosis, dict):
            raise TypeError("Diagnosis must be a dictionary.")

        category = diagnosis.get("category")

        if not isinstance(category, str) or not category.strip():
            raise ValueError("Diagnosis must contain a valid failure category.")

        action = self.RECOVERY_ACTIONS.get(
            category,
            self.RECOVERY_ACTIONS["unknown_failure"],
        )

        return {
            "failure_category": category,
            "action_id": action["action_id"],
            "description": action["description"],
            "risk_level": action["risk_level"],
            "requires_approval": action["requires_approval"],
            "status": ("awaiting_approval" if action["requires_approval"] else "ready"),
        }
