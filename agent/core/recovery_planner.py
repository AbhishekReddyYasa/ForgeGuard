from typing import Any


class RecoveryPlanner:
    """Generate predefined recovery proposals from failure diagnoses."""

    RECOVERY_ACTIONS = {
        "test_failure": {
            "action_id": "inspect_test_failure",
            "description": "Inspect the failing test and related application code.",
            "risk_level": "low",
            "requires_approval": True,
        },
        "lint_failure": {
            "action_id": "review_lint_violations",
            "description": "Review and correct the reported lint violations.",
            "risk_level": "medium",
            "requires_approval": True,
        },
        "format_failure": {
            "action_id": "run_code_formatter",
            "description": "Run the configured code formatter on the affected files.",
            "risk_level": "medium",
            "requires_approval": True,
        },
        "timeout": {
            "action_id": "review_timeout",
            "description": "Inspect execution duration and review timeout settings.",
            "risk_level": "low",
            "requires_approval": True,
        },
        "execution_error": {
            "action_id": "inspect_execution_environment",
            "description": "Check dependencies and execution configuration.",
            "risk_level": "low",
            "requires_approval": True,
        },
        "unknown_failure": {
            "action_id": "manual_investigation",
            "description": "Request manual investigation because the failure is not recognised.",
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
            "status": "awaiting_approval",
        }
