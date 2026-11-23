import pytest
from agent.core.recovery_planner import RecoveryPlanner


@pytest.fixture
def planner():
    return RecoveryPlanner()


@pytest.mark.parametrize(
    ("category", "expected_action"),
    [
        ("test_failure", "inspect_test_failure"),
        ("lint_failure", "review_lint_violations"),
        ("format_failure", "run_code_formatter"),
        ("timeout", "review_timeout"),
        ("execution_error", "inspect_execution_environment"),
        ("unknown_failure", "manual_investigation"),
    ],
)
def test_creates_correct_recovery_plan(planner, category, expected_action):
    diagnosis = {"category": category}

    plan = planner.create_plan(diagnosis)

    assert plan["failure_category"] == category
    assert plan["action_id"] == expected_action


def test_recovery_plan_requires_human_approval(planner):
    plan = planner.create_plan({"category": "test_failure"})

    assert plan["requires_approval"] is True
    assert plan["status"] == "awaiting_approval"


def test_unknown_category_uses_manual_investigation(planner):
    plan = planner.create_plan({"category": "database_failure"})

    assert plan["action_id"] == "manual_investigation"
    assert plan["status"] == "awaiting_approval"


def test_recovery_plan_contains_risk_level(planner):
    plan = planner.create_plan({"category": "lint_failure"})

    assert plan["risk_level"] == "medium"


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
