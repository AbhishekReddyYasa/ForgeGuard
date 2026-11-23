import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ActionDefinition:
    """Describe an operation permitted by ForgeGuard."""

    action_id: str
    description: str
    modifies_files: bool
    requires_approval: bool
    arguments: tuple[str, ...]


class ActionRegistry:
    """Register and validate predefined recovery actions."""

    ACTIONS = {
        "run_python_tests": ActionDefinition(
            action_id="run_python_tests",
            description="Run the project's Python test suite.",
            modifies_files=False,
            requires_approval=False,
            arguments=("-m", "pytest", "-q"),
        ),
        "run_ruff_lint": ActionDefinition(
            action_id="run_ruff_lint",
            description="Run Ruff lint checks on the project.",
            modifies_files=False,
            requires_approval=False,
            arguments=("-m", "ruff", "check", "."),
        ),
        "format_python_file": ActionDefinition(
            action_id="format_python_file",
            description="Format one approved Python file using Ruff.",
            modifies_files=True,
            requires_approval=True,
            arguments=("-m", "ruff", "format"),
        ),
    }

    def get_action(self, action_id: str) -> ActionDefinition:
        """Return a registered action or reject an unknown action."""

        if not isinstance(action_id, str) or not action_id.strip():
            raise ValueError("Action ID must be a non-empty string.")

        if action_id not in self.ACTIONS:
            raise ValueError(f"Action '{action_id}' is not registered.")

        return self.ACTIONS[action_id]

    def list_actions(self) -> list[ActionDefinition]:
        """Return all registered actions."""

        return list(self.ACTIONS.values())

    def build_command(
        self,
        action_id: str,
        target: str | Path | None = None,
    ) -> list[str]:
        """Build a command using only predefined executable arguments."""

        action = self.get_action(action_id)

        if action.modifies_files:
            if target is None:
                raise ValueError("A target file is required for this action.")

            command = [sys.executable, *action.arguments, str(target)]

        else:
            if target is not None:
                raise ValueError("This action does not accept a target file.")

            command = [sys.executable, *action.arguments]

        return command
