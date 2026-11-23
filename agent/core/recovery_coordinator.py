from pathlib import Path
from typing import Any

from agent.core.failure_diagnoser import FailureDiagnoser
from agent.core.recovery_planner import RecoveryPlanner
from harness.security.approval_gate import ApprovalGate
from harness.security.controlled_executor import ControlledExecutor


class RecoveryCoordinator:
    """Coordinate diagnosis, recovery planning, approval, and execution."""

    def __init__(self, workspace: Path | None = None) -> None:
        self.diagnoser = FailureDiagnoser()
        self.planner = RecoveryPlanner()
        self.approval_gate = ApprovalGate()
        self.executor = ControlledExecutor(
            workspace=workspace or Path.cwd(),
        )

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
        """Check whether a proposal is permitted to execute."""

        if not isinstance(proposal, dict):
            return False

        recovery_plan = proposal.get("recovery_plan")

        return self.approval_gate.can_execute(recovery_plan)

    def execute_recovery(
        self,
        proposal: dict[str, Any],
        target: str | Path | None = None,
    ) -> dict[str, Any]:
        """Execute an approved recovery action through the controlled executor."""

        if not isinstance(proposal, dict):
            raise TypeError("Proposal must be a dictionary.")

        recovery_plan = proposal.get("recovery_plan")

        if not isinstance(recovery_plan, dict):
            raise ValueError("Proposal must contain a valid recovery plan.")

        if not self.can_execute(proposal):
            raise PermissionError("Recovery proposal is not approved or ready for execution.")

        action_id = recovery_plan.get("action_id")
        requires_approval = recovery_plan.get("requires_approval")

        result = self.executor.execute(
            action_id=action_id,
            approved=requires_approval is True,
            target=target,
        )

        updated_plan = recovery_plan.copy()
        updated_plan["status"] = "executed" if result["passed"] else "failed"

        updated_proposal = proposal.copy()
        updated_proposal["recovery_plan"] = updated_plan
        updated_proposal["execution_result"] = result

        return updated_proposal
