import json
from pathlib import Path

from agent.core.recovery_coordinator import RecoveryCoordinator
from harness.observability.execution_history import ExecutionHistory

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Demonstrate ForgeGuard's diagnosis and controlled recovery workflow."""

    workspace = PROJECT_ROOT

    print("=" * 65)
    print("                 FORGEGUARD DEMONSTRATION")
    print("=" * 65)

    simulated_failure = "AssertionError: Expected 10 but received 8"

    print("\n[1] SIMULATED FAILURE")
    print(simulated_failure)

    coordinator = RecoveryCoordinator(workspace=workspace)
    proposal = coordinator.create_recovery_proposal(simulated_failure)

    print("\n[2] FAILURE DIAGNOSIS")
    print(json.dumps(proposal["diagnosis"], indent=4))

    print("\n[3] RECOVERY PROPOSAL")
    print(json.dumps(proposal["recovery_plan"], indent=4))

    if not coordinator.can_execute(proposal):
        print("\n[4] EXECUTION BLOCKED")
        print("The recovery proposal is not permitted to execute.")
        raise SystemExit(1)

    print("\n[4] APPROVAL CHECK")
    print("Passed: read-only action does not require human approval.")

    print("\n[5] CONTROLLED RECOVERY")
    print("Rerunning the project's Python test suite...")

    result = coordinator.execute_recovery(proposal)

    print("\n[6] EXECUTION RESULT")
    print(json.dumps(result["execution_result"], indent=4))

    print("\n[7] UPDATED RECOVERY STATUS")
    print(result["recovery_plan"]["status"])

    log_file = workspace / "reports" / "execution_log.jsonl"
    history = ExecutionHistory(log_file)

    records = history.load()
    statistics = history.get_statistics()

    print("\n[8] EXECUTION HISTORY")
    print(f"Total recorded executions: {statistics['total']}")
    print(f"Successful executions: {statistics['successful']}")
    print(f"Failed executions: {statistics['failed']}")
    print(f"Success rate: {statistics['success_rate']}%")

    if records:
        print("\nLatest execution record:")
        print(json.dumps(records[-1], indent=4))

    if not result["execution_result"]["passed"]:
        print("\nDEMONSTRATION FAILED: Verification detected errors.")
        raise SystemExit(1)

    print("\n" + "=" * 65)
    print("                 DEMONSTRATION COMPLETE")
    print("=" * 65)


if __name__ == "__main__":
    main()
