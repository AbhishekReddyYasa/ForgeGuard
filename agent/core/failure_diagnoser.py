class FailureDiagnoser:
    """Identify common verification failures using predefined rules."""

    FAILURE_RULES = {
        "test_failure": {
            "patterns": ["AssertionError", "FAILED", "failed"],
            "description": "One or more automated tests failed.",
            "suggestion": ("Inspect the failing test and compare expected and actual results."),
        },
        "lint_failure": {
            "patterns": ["ruff check", "I001", "F401", "E501"],
            "description": "The code contains a linting issue.",
            "suggestion": (
                "Inspect the reported file and line, then correct the code-quality issue."
            ),
        },
        "format_failure": {
            "patterns": ["would be reformatted", "unformatted:"],
            "description": "One or more files do not follow the required formatting.",
            "suggestion": ("Run the configured formatter and verify the changes."),
        },
        "timeout": {
            "patterns": ["timed out", "TimeoutExpired"],
            "description": "The verification command exceeded its time limit.",
            "suggestion": (
                "Inspect the command and determine whether it needs more time or is stuck."
            ),
        },
        "execution_error": {
            "patterns": [
                "ModuleNotFoundError",
                "ImportError",
                "No module named",
                "command not found",
            ],
            "description": (
                "The verification command encountered an execution or dependency error."
            ),
            "suggestion": (
                "Check the Python environment, installed dependencies, and command configuration."
            ),
        },
    }

    def diagnose(self, output: str) -> dict:
        """Identify all recognised failure categories in verification output."""

        if not output.strip():
            return {
                "category": "unknown_failure",
                "description": "No error output was provided.",
                "suggestion": (
                    "Inspect the verification process for additional diagnostic information."
                ),
                "detected_issues": [],
            }

        normalized_output = output.lower()
        detected_issues = []

        for category, rule in self.FAILURE_RULES.items():
            if any(pattern.lower() in normalized_output for pattern in rule["patterns"]):
                detected_issues.append(
                    {
                        "category": category,
                        "description": rule["description"],
                        "suggestion": rule["suggestion"],
                    }
                )

        if not detected_issues:
            return {
                "category": "unknown_failure",
                "description": "The failure does not match any recognised pattern.",
                "suggestion": ("Inspect the complete verification output to identify the cause."),
                "detected_issues": [],
            }

        primary_issue = detected_issues[0]

        return {
            "category": primary_issue["category"],
            "description": primary_issue["description"],
            "suggestion": primary_issue["suggestion"],
            "detected_issues": detected_issues,
        }
