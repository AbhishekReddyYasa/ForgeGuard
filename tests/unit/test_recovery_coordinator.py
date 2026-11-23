import pytest
from agent.core.recovery_coordinator import RecoveryCoordinator


@pytest.fixture
def coordinator():
    return RecoveryCoordinator()


@pytest.fixture
def proposal(coordinator):
    return coordinator.create_recovery_proposal("AssertionError: Expected 10 but received 8")


def test_creates_recovery_proposal(coordinator):
    result = coordinator.create_recovery_proposal("AssertionError: Expected 10 but received 8")

    assert result["diagnosis"]["category"] == "test_failure"
    assert result["recovery_plan"]["action_id"] == "inspect_test_failure"


def test_proposal_awaits_approval(proposal):
    assert proposal["recovery_plan"]["status"] == "awaiting_approval"
    assert proposal["recovery_plan"]["requires_approval"] is True


def test_unapproved_proposal_cannot_execute(coordinator, proposal):
    assert coordinator.can_execute(proposal) is False


def test_approved_proposal_can_pass_approval_gate(coordinator, proposal):
    approved = coordinator.record_approval(proposal, "approved")

    assert approved["recovery_plan"]["approval_status"] == "approved"
    assert coordinator.can_execute(approved) is True


def test_rejected_proposal_cannot_execute(coordinator, proposal):
    rejected = coordinator.record_approval(proposal, "rejected")

    assert rejected["recovery_plan"]["status"] == "rejected"
    assert coordinator.can_execute(rejected) is False


def test_pending_proposal_cannot_execute(coordinator, proposal):
    pending = coordinator.record_approval(proposal, "pending")

    assert coordinator.can_execute(pending) is False


def test_invalid_approval_decision_is_rejected(coordinator, proposal):
    with pytest.raises(ValueError):
        coordinator.record_approval(proposal, "maybe")


def test_invalid_output_type_is_rejected(coordinator):
    with pytest.raises(TypeError):
        coordinator.create_recovery_proposal(123)


def test_invalid_proposal_is_rejected(coordinator):
    with pytest.raises(TypeError):
        coordinator.record_approval("invalid", "approved")


def test_original_proposal_remains_unchanged(coordinator, proposal):
    approved = coordinator.record_approval(proposal, "approved")

    assert proposal["recovery_plan"]["status"] == "awaiting_approval"
    assert "approval_status" not in proposal["recovery_plan"]
    assert approved["recovery_plan"]["status"] == "approved"


def test_empty_output_creates_unknown_failure_proposal(coordinator):
    result = coordinator.create_recovery_proposal("")

    assert result["diagnosis"]["category"] == "unknown_failure"
    assert result["recovery_plan"]["action_id"] == "manual_investigation"
    assert coordinator.can_execute(result) is False
