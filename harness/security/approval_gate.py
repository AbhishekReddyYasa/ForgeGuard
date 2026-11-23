from typing import Any


class ApprovalGate:
    """Control approval for actions that modify project files."""

    APPROVAL_STATUSES = {
        "approved",
        "rejected",
        "pending",
    }

    def approve(
        self,
        recovery_plan: dict[str, Any],
        decision: str,
    ) -> dict[str, Any]:
        """Record an explicit approval or rejection."""

        if not isinstance(recovery_plan, dict):
            raise TypeError("Recovery plan must be a dictionary.")

        action_id = recovery_plan.get("action_id")

        if not isinstance(action_id, str) or not action_id.strip():
            raise ValueError("Recovery plan must contain a valid action ID.")

        if decision not in self.APPROVAL_STATUSES:
            raise ValueError("Decision must be 'approved', 'rejected', or 'pending'.")

        updated_plan = recovery_plan.copy()
        updated_plan["approval_status"] = decision

        if decision == "approved":
            updated_plan["status"] = "approved"
        elif decision == "rejected":
            updated_plan["status"] = "rejected"
        else:
            updated_plan["status"] = "awaiting_approval"

        return updated_plan

    def can_execute(self, recovery_plan: dict[str, Any]) -> bool:
        """Allow read-only actions directly and require approval for modifications."""

        if not isinstance(recovery_plan, dict):
            return False

        if recovery_plan.get("requires_approval") is False:
            return recovery_plan.get("status") == "ready"

        return (
            recovery_plan.get("requires_approval") is True
            and recovery_plan.get("approval_status") == "approved"
            and recovery_plan.get("status") == "approved"
        )
