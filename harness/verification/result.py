
from dataclasses import dataclass


@dataclass
class VerificationResult:
    """Store the outcome of a single verification check."""

    check_name: str
    passed: bool
    duration_seconds: float
    output: str

    def __post_init__(self) -> None:
        if not self.check_name.strip():
            raise ValueError("Check name cannot be empty.")

        if self.duration_seconds < 0:
            raise ValueError("Duration cannot be negative.")
