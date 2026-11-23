# ForgeGuard - Agent Instructions

## Project Overview

ForgeGuard is a Python-based autonomous software reliability engineering framework.

Its purpose is to execute software maintenance tasks using controlled tools, automated verification, security policies and persistent execution records.

## Project Structure

- agent/: Agent orchestration and execution
- agent/core/: Planning and task management
- agent/tools/: Controlled agent tools
- agent/memory/: Persistent agent memory
- harness/: Reliability infrastructure
- harness/verification/: Automated verification
- harness/security/: Permissions and safety
- harness/observability/: Logs and execution traces
- config/: Configuration files
- docs/: Project specifications and documentation
- tests/: Automated tests
- tests/unit/: Unit tests
- tests/integration/: Integration tests
- benchmarks/: Repeatable evaluation tasks
- workspace/: Isolated task execution area
- reports/: Generated execution reports
- scripts/: Utility scripts

## Development Environment

- Python: 3.13
- Virtual environment: .venv

## Commands

- Activate: .venv\\Scripts\\activate
- Install: pip install -r requirements.txt
- Test: pytest -q
- Lint: ruff check .
- Format: ruff format .
- Verify: ruff check . && pytest -q

## Engineering Rules

1. Keep components modular and focused.
2. Validate external inputs before processing.
3. Keep secrets outside source control.
4. Use pathlib for filesystem operations.
5. Use explicit error handling.
6. Record important tool executions.
7. Keep execution within the assigned workspace.
8. Prefer deterministic verification checks.

## Safety Rules

- Never read or expose .env files.
- Never access files outside the assigned workspace without explicit authorization.
- Never execute unrestricted destructive commands.
- Require approval for consequential operations.
- Never modify or delete tests merely to make verification pass.
- Do not commit secrets, credentials or API keys.

## Before Declaring a Task Complete

- Run the relevant automated tests.
- Run the configured lint checks.
- Inspect the final changes.
- Report any remaining failures honestly.
- Record the execution outcome.

## Do Not

- Do not disable verification to obtain a passing result.
- Do not silently overwrite existing project files.
- Do not add dependencies without justification.
- Do not bypass security restrictions.
