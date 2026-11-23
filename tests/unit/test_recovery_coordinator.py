from unittest.mock import Mock

import pytest
from agent.core.recovery_coordinator import RecoveryCoordinator


@pytest.fixture
def coordinator(tmp_path):
    return RecoveryCoordinator(workspace=tmp_path)


@pytest.fixture
def proposal(coordinator):
    return coordinator.create_recovery_proposal("AssertionError: Expected 10 but received 8")


@pytest.fixture
def modifying_proposal(coordinator):
    return coordinator.create_recovery_proposal("would be reformatted: example.py")


def test_creates_recovery_proposal(coordinator):
    result = coordinator.create_recovery_proposal("AssertionError: Expected 10 but received 8")

    assert result["diagnosis"]["category"] == "test_failure"
    assert result["recovery_plan"]["action_id"] == "run_python_tests"
    assert result["recovery_plan"]["status"] == "ready"


def test_read_only_proposal_can_execute_without_approval(coordinator, proposal):
    assert coordinator.can_execute(proposal) is True


def test_modifying_proposal_awaits_approval(modifying_proposal):
    plan = modifying_proposal["recovery_plan"]

    assert plan["action_id"] == "format_python_file"
    assert plan["requires_approval"] is True
    assert plan["status"] == "awaiting_approval"


def test_unapproved_modifying_proposal_cannot_execute(
    coordinator,
    modifying_proposal,
):
    assert coordinator.can_execute(modifying_proposal) is False


def test_approved_proposal_can_pass_approval_gate(
    coordinator,
    modifying_proposal,
):
    approved = coordinator.record_approval(modifying_proposal, "approved")

    assert approved["recovery_plan"]["approval_status"] == "approved"
    assert coordinator.can_execute(approved) is True


def test_rejected_proposal_cannot_execute(
    coordinator,
    modifying_proposal,
):
    rejected = coordinator.record_approval(modifying_proposal, "rejected")

    assert rejected["recovery_plan"]["status"] == "rejected"
    assert coordinator.can_execute(rejected) is False


def test_pending_proposal_cannot_execute(
    coordinator,
    modifying_proposal,
):
    pending = coordinator.record_approval(modifying_proposal, "pending")

    assert coordinator.can_execute(pending) is False


def test_invalid_approval_decision_is_rejected(
    coordinator,
    modifying_proposal,
):
    with pytest.raises(ValueError):
        coordinator.record_approval(modifying_proposal, "maybe")


def test_invalid_output_type_is_rejected(coordinator):
    with pytest.raises(TypeError):
        coordinator.create_recovery_proposal(123)


def test_invalid_proposal_is_rejected(coordinator):
    with pytest.raises(TypeError):
        coordinator.record_approval("invalid", "approved")


def test_original_proposal_remains_unchanged(
    coordinator,
    modifying_proposal,
):
    approved = coordinator.record_approval(modifying_proposal, "approved")

    assert modifying_proposal["recovery_plan"]["status"] == "awaiting_approval"
    assert "approval_status" not in modifying_proposal["recovery_plan"]
    assert approved["recovery_plan"]["status"] == "approved"


def test_empty_output_creates_unknown_failure_proposal(coordinator):
    result = coordinator.create_recovery_proposal("")

    assert result["diagnosis"]["category"] == "unknown_failure"
    assert result["recovery_plan"]["action_id"] == "manual_investigation"
    assert coordinator.can_execute(result) is False


def test_execute_recovery_runs_read_only_action(coordinator, proposal):
    coordinator.executor.execute = Mock(
        return_value={
            "action_id": "run_python_tests",
            "passed": True,
            "return_code": 0,
            "duration_seconds": 0.5,
            "output": "Tests passed.",
        }
    )

    result = coordinator.execute_recovery(proposal)

    coordinator.executor.execute.assert_called_once_with(
        action_id="run_python_tests",
        approved=False,
        target=None,
    )
    assert result["execution_result"]["passed"] is True
    assert result["recovery_plan"]["status"] == "executed"
    assert proposal["recovery_plan"]["status"] == "ready"


def test_execute_recovery_blocks_unapproved_modification(
    coordinator,
    modifying_proposal,
    tmp_path,
):
    target = tmp_path / "example.py"
    target.write_text("print('hello')\n", encoding="utf-8")

    with pytest.raises(PermissionError):
        coordinator.execute_recovery(
            modifying_proposal,
            target=target,
        )


def test_execute_recovery_runs_approved_modification(
    coordinator,
    modifying_proposal,
    tmp_path,
):
    target = tmp_path / "example.py"
    target.write_text("print( 'hello' )\n", encoding="utf-8")

    approved = coordinator.record_approval(modifying_proposal, "approved")

    coordinator.executor.execute = Mock(
        return_value={
            "action_id": "format_python_file",
            "passed": True,
            "return_code": 0,
            "duration_seconds": 0.2,
            "output": "1 file reformatted.",
        }
    )

    result = coordinator.execute_recovery(approved, target=target)

    coordinator.executor.execute.assert_called_once_with(
        action_id="format_python_file",
        approved=True,
        target=target,
    )
    assert result["execution_result"]["passed"] is True
    assert result["recovery_plan"]["status"] == "executed"


def test_execute_recovery_records_failed_execution(coordinator, proposal):
    coordinator.executor.execute = Mock(
        return_value={
            "action_id": "run_python_tests",
            "passed": False,
            "return_code": 1,
            "duration_seconds": 0.4,
            "output": "Tests failed.",
        }
    )

    result = coordinator.execute_recovery(proposal)

    assert result["execution_result"]["passed"] is False
    assert result["recovery_plan"]["status"] == "failed"
