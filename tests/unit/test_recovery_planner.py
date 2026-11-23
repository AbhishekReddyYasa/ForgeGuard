import pytest
from agent.core.recovery_planner import RecoveryPlanner


@pytest.fixture
def planner():
    return RecoveryPlanner()


@pytest.mark.parametrize(
    ("category", "expected_action", "requires_approval"),
    [
        ("test_failure", "run_python_tests", False),
        ("lint_failure", "run_ruff_lint", False),
        ("format_failure", "format_python_file", True),
        ("timeout", "manual_investigation", True),
        ("execution_error", "manual_investigation", True),
        ("unknown_failure", "manual_investigation", True),
    ],
)
def test_creates_correct_recovery_plan(
    planner,
    category,
    expected_action,
    requires_approval,
):
    plan = planner.create_plan({"category": category})

    assert plan["failure_category"] == category
    assert plan["action_id"] == expected_action
    assert plan["requires_approval"] is requires_approval


def test_read_only_recovery_is_ready(planner):
    plan = planner.create_plan({"category": "test_failure"})

    assert plan["requires_approval"] is False
    assert plan["status"] == "ready"


def test_modifying_recovery_awaits_approval(planner):
    plan = planner.create_plan({"category": "format_failure"})

    assert plan["requires_approval"] is True
    assert plan["status"] == "awaiting_approval"


def test_unknown_category_uses_manual_investigation(planner):
    plan = planner.create_plan({"category": "database_failure"})

    assert plan["action_id"] == "manual_investigation"
    assert plan["status"] == "awaiting_approval"


def test_recovery_plan_contains_risk_level(planner):
    plan = planner.create_plan({"category": "lint_failure"})

    assert plan["risk_level"] == "low"


def test_rejects_non_dictionary_diagnosis(planner):
    with pytest.raises(TypeError):
        planner.create_plan("test_failure")


@pytest.mark.parametrize(
    "diagnosis",
    [
        {},
        {"category": ""},
        {"category": None},
        {"category": 123},
    ],
)
def test_rejects_missing_or_invalid_category(planner, diagnosis):
    with pytest.raises(ValueError):
        planner.create_plan(diagnosis)
