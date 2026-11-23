from typing import Any


class ApprovalGate:
    """Control whether a proposed recovery action has human approval."""

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
        """Record an explicit approval or rejection for a recovery plan."""

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
        """Check whether a recovery plan has explicit human approval."""

        if not isinstance(recovery_plan, dict):
            return False

        return (
            recovery_plan.get("approval_status") == "approved"
            and recovery_plan.get("status") == "approved"
            and recovery_plan.get("requires_approval") is True
        )
