import pytest
from agent.core.recovery_planner import RecoveryPlanner
from harness.security.approval_gate import ApprovalGate


@pytest.fixture
def gate():
    return ApprovalGate()


@pytest.fixture
def recovery_plan():
    return RecoveryPlanner().create_plan({"category": "test_failure"})


def test_approved_plan_can_proceed(gate, recovery_plan):
    approved = gate.approve(recovery_plan, "approved")

    assert approved["approval_status"] == "approved"
    assert approved["status"] == "approved"
    assert gate.can_execute(approved) is True


def test_rejected_plan_cannot_proceed(gate, recovery_plan):
    rejected = gate.approve(recovery_plan, "rejected")

    assert rejected["approval_status"] == "rejected"
    assert rejected["status"] == "rejected"
    assert gate.can_execute(rejected) is False


def test_pending_plan_cannot_proceed(gate, recovery_plan):
    pending = gate.approve(recovery_plan, "pending")

    assert pending["approval_status"] == "pending"
    assert pending["status"] == "awaiting_approval"
    assert gate.can_execute(pending) is False


def test_plan_without_approval_cannot_proceed(gate, recovery_plan):
    assert gate.can_execute(recovery_plan) is False


def test_invalid_decision_is_rejected(gate, recovery_plan):
    with pytest.raises(ValueError):
        gate.approve(recovery_plan, "maybe")


def test_non_dictionary_plan_is_rejected(gate):
    with pytest.raises(TypeError):
        gate.approve("invalid", "approved")


def test_plan_without_action_id_is_rejected(gate):
    with pytest.raises(ValueError):
        gate.approve({}, "approved")


def test_approval_does_not_modify_original_plan(gate, recovery_plan):
    original_status = recovery_plan["status"]

    gate.approve(recovery_plan, "approved")

    assert recovery_plan["status"] == original_status
    assert "approval_status" not in recovery_plan


def test_non_dictionary_cannot_execute(gate):
    assert gate.can_execute("invalid") is False


def test_approval_requires_requires_approval_flag(gate, recovery_plan):
    approved = gate.approve(recovery_plan, "approved")
    approved["requires_approval"] = False

    assert gate.can_execute(approved) is False


def test_forged_status_without_approval_is_blocked(gate, recovery_plan):
    recovery_plan["status"] = "approved"

    assert gate.can_execute(recovery_plan) is False
