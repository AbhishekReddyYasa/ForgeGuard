import pytest
from agent.core.recovery_planner import RecoveryPlanner
from harness.security.approval_gate import ApprovalGate


@pytest.fixture
def gate():
    return ApprovalGate()


@pytest.fixture
def read_only_plan():
    return RecoveryPlanner().create_plan({"category": "test_failure"})


@pytest.fixture
def modifying_plan():
    return RecoveryPlanner().create_plan({"category": "format_failure"})


def test_approved_modifying_plan_can_proceed(gate, modifying_plan):
    approved = gate.approve(modifying_plan, "approved")

    assert approved["approval_status"] == "approved"
    assert approved["status"] == "approved"
    assert gate.can_execute(approved) is True


def test_rejected_modifying_plan_cannot_proceed(gate, modifying_plan):
    rejected = gate.approve(modifying_plan, "rejected")

    assert rejected["approval_status"] == "rejected"
    assert rejected["status"] == "rejected"
    assert gate.can_execute(rejected) is False


def test_pending_modifying_plan_cannot_proceed(gate, modifying_plan):
    pending = gate.approve(modifying_plan, "pending")

    assert pending["approval_status"] == "pending"
    assert pending["status"] == "awaiting_approval"
    assert gate.can_execute(pending) is False


def test_read_only_plan_can_proceed_without_approval(gate, read_only_plan):
    assert read_only_plan["requires_approval"] is False
    assert gate.can_execute(read_only_plan) is True


def test_invalid_decision_is_rejected(gate, modifying_plan):
    with pytest.raises(ValueError):
        gate.approve(modifying_plan, "maybe")


def test_non_dictionary_plan_is_rejected(gate):
    with pytest.raises(TypeError):
        gate.approve("invalid", "approved")


def test_plan_without_action_id_is_rejected(gate):
    with pytest.raises(ValueError):
        gate.approve({}, "approved")


def test_approval_does_not_modify_original_plan(gate, modifying_plan):
    original_status = modifying_plan["status"]

    gate.approve(modifying_plan, "approved")

    assert modifying_plan["status"] == original_status
    assert "approval_status" not in modifying_plan


def test_non_dictionary_cannot_execute(gate):
    assert gate.can_execute("invalid") is False


def test_modifying_plan_requires_explicit_approval(gate, modifying_plan):
    assert gate.can_execute(modifying_plan) is False


def test_forged_status_without_approval_is_blocked(gate, modifying_plan):
    modifying_plan["status"] = "approved"

    assert gate.can_execute(modifying_plan) is False


def test_read_only_plan_with_forged_status_is_blocked(gate, read_only_plan):
    read_only_plan["status"] = "approved"

    assert gate.can_execute(read_only_plan) is False
