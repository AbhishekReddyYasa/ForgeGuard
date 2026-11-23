import pytest
from harness.security.action_registry import ActionRegistry


@pytest.fixture
def registry():
    return ActionRegistry()


def test_registry_contains_three_actions(registry):
    assert len(registry.list_actions()) == 3


@pytest.mark.parametrize(
    "action_id",
    ["run_python_tests", "run_ruff_lint", "format_python_file"],
)
def test_registered_actions_can_be_retrieved(registry, action_id):
    assert registry.get_action(action_id).action_id == action_id


def test_unknown_action_is_rejected(registry):
    with pytest.raises(ValueError):
        registry.get_action("delete_everything")


def test_invalid_action_id_is_rejected(registry):
    with pytest.raises(ValueError):
        registry.get_action("")


def test_read_only_actions_do_not_require_approval(registry):
    assert registry.get_action("run_python_tests").requires_approval is False
    assert registry.get_action("run_ruff_lint").requires_approval is False


def test_formatting_requires_approval(registry):
    action = registry.get_action("format_python_file")

    assert action.modifies_files is True
    assert action.requires_approval is True


def test_test_command_uses_current_python(registry):
    command = registry.build_command("run_python_tests")

    assert command[0].endswith("python.exe")
    assert command[1:] == ["-m", "pytest", "-q"]


def test_lint_command_is_predefined(registry):
    command = registry.build_command("run_ruff_lint")

    assert command[1:] == ["-m", "ruff", "check", "."]


def test_format_command_requires_target(registry):
    with pytest.raises(ValueError):
        registry.build_command("format_python_file")


def test_format_command_accepts_target(registry):
    command = registry.build_command(
        "format_python_file",
        "agent/core/example.py",
    )

    assert command[1:] == ["-m", "ruff", "format", "agent/core/example.py"]


def test_read_only_command_rejects_target(registry):
    with pytest.raises(ValueError):
        registry.build_command("run_python_tests", "example.py")
