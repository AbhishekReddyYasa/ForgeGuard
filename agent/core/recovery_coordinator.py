from typing import Any

from agent.core.failure_diagnoser import FailureDiagnoser
from agent.core.recovery_planner import RecoveryPlanner
from harness.security.approval_gate import ApprovalGate


class RecoveryCoordinator:
    """Coordinate failure diagnosis, recovery planning, and approval."""

    def __init__(self) -> None:
        self.diagnoser = FailureDiagnoser()
        self.planner = RecoveryPlanner()
        self.approval_gate = ApprovalGate()

    def create_recovery_proposal(self, output: str) -> dict[str, Any]:
        """Diagnose a failure and create a recovery proposal."""

        if not isinstance(output, str):
            raise TypeError("Failure output must be a string.")

        diagnosis = self.diagnoser.diagnose(output)
        recovery_plan = self.planner.create_plan(diagnosis)

        return {
            "diagnosis": diagnosis,
            "recovery_plan": recovery_plan,
        }

    def record_approval(
        self,
        proposal: dict[str, Any],
        decision: str,
    ) -> dict[str, Any]:
        """Record a human decision for a recovery proposal."""

        if not isinstance(proposal, dict):
            raise TypeError("Proposal must be a dictionary.")

        recovery_plan = proposal.get("recovery_plan")

        if not isinstance(recovery_plan, dict):
            raise ValueError("Proposal must contain a valid recovery plan.")

        updated_plan = self.approval_gate.approve(recovery_plan, decision)

        updated_proposal = proposal.copy()
        updated_proposal["recovery_plan"] = updated_plan

        return updated_proposal

    def can_execute(self, proposal: dict[str, Any]) -> bool:
        """Check whether a proposal has passed the approval gate."""

        if not isinstance(proposal, dict):
            return False

        recovery_plan = proposal.get("recovery_plan")

        return self.approval_gate.can_execute(recovery_plan)
