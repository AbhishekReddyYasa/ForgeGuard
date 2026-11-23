# ForgeGuard 🛡️

**A Python-based agent harness for identifying software failures and handling recovery in a controlled way.**

Software development doesn't always go smoothly. Tests fail, code formatting gets messed up, and sometimes tracking down a small issue takes longer than actually fixing it.

I started building ForgeGuard to explore how an agent-based system could make this process easier. The goal was to create something that could identify common software issues, figure out what might have caused them, suggest a suitable fix, and carry out the required action with the right permissions.

An important part of the project is control. Instead of allowing an agent to execute any command it wants, ForgeGuard uses predefined actions and approval checks to keep recovery operations restricted and traceable.

## What does ForgeGuard do?

- **Failure detection:** Identifies common development issues, including failed tests, linting errors, formatting problems, and execution timeouts.
- **Recovery planning:** Suggests an appropriate action based on the type of failure detected.
- **Permission checks:** Allows safe, read-only operations while requiring approval for actions that modify files.
- **Controlled execution:** Executes only registered actions rather than accepting arbitrary commands.
- **Execution history:** Keeps track of executed actions, their results, execution time, and output.
- **Verification:** Uses tools like Pytest and Ruff to check whether the project is working as expected.

## How does it work?

ForgeGuard follows a simple sequence, with each component handling a specific part of the recovery process.

1. A software failure is reported to the system.
2. The failure diagnoser analyses the error and identifies its category.
3. The recovery planner decides what action should be taken.
4. The approval gate checks whether the proposed action is permitted.
5. The controlled executor runs the approved action.
6. The result is recorded in the execution log.
7. The execution history can be reviewed later.

### Workflow

```text
       Software Failure
              |
              v
       Failure Diagnoser
              |
              v
        Recovery Planner
              |
              v
         Approval Gate
              |
              v
      Controlled Executor
              |
              v
       Verification Checks
              |
              v
       Execution Logger
              |
              v
       Execution History
```

## Available recovery actions

At the moment, ForgeGuard supports three predefined recovery actions.

| Action | Description | Approval |
|---|---|---|
| `run_python_tests` | Runs the project's test suite | Not required |
| `run_ruff_lint` | Checks the code for linting issues | Not required |
| `format_python_file` | Formats a selected Python file | Required |

These actions are maintained in an action registry. This means the executor can only run operations that have been explicitly registered. If an unknown action is requested, it gets rejected.

## Technologies used

- Python 3.13
- Pytest for testing
- Ruff for linting and formatting
- SQLAlchemy
- Pydantic
- PyYAML
- Git for version control

## Getting started

To run ForgeGuard locally, you'll need Python 3.13 or later and Git installed.

**1. Clone the repository**

```cmd
git clone <repository-url>
cd ForgeGuard
```

**2. Create and activate a virtual environment**

```cmd
python -m venv .venv
.venv\Scripts\activate
```

**3. Install the required dependencies**

```cmd
python -m pip install -r requirements.txt
```

## Running ForgeGuard

If you want to see how everything fits together, start with the demo:

```cmd
python -m scripts.demo
```

The demo simulates a test failure and takes it through the recovery workflow. It diagnoses the issue, prepares a recovery plan, checks whether the action is allowed, and then runs the test suite through the controlled executor.

Once the execution is complete, it also displays the result and some execution history statistics.

You can also run the individual checks separately.

**Run the tests**

```cmd
python -m pytest -q
```

**Check for linting issues**

```cmd
python -m ruff check .
```

**Check code formatting**

```cmd
python -m ruff format --check .
```

## Project structure

```text
ForgeGuard/
│
├── agent/
│   ├── core/
│   │   ├── failure_diagnoser.py
│   │   ├── diagnosis_coordinator.py
│   │   ├── recovery_planner.py
│   │   └── recovery_coordinator.py
│   ├── tools/
│   └── memory/
│
├── harness/
│   ├── verification/
│   ├── security/
│   └── observability/
│
├── tests/
│   ├── unit/
│   └── integration/
│
├── scripts/
│   └── demo.py
│
├── docs/
├── config/
├── benchmarks/
├── workspace/
├── reports/
│
├── AGENTS.md
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Testing results

During development, the latest full test run produced the following results:

| Result | Count |
|---|---:|
| Tests collected | 115 |
| Passed | 114 |
| Failed | 0 |
| Skipped | 1 |

The only skipped test is related to symbolic-link availability in the Windows environment.

## Security and limitations

One of the things I wanted to get right while building ForgeGuard was making sure that an agent could use useful tools without having unrestricted access to the system.

To handle this, the current implementation includes:

- A predefined registry of allowed actions.
- Approval checks before file-modifying operations.
- Workspace path validation for formatting targets.
- Execution timeouts to prevent operations from running indefinitely.
- `shell=False` when launching subprocesses.
- Execution logs to keep track of what happened.

There are a few limitations worth mentioning.

ForgeGuard currently runs with the permissions of the Windows user executing it. This means the workspace is not an isolated operating-system sandbox. The approval mechanism is also an application-level permission check, not a full authentication or security system.

Another limitation is that failure diagnosis currently uses predefined error patterns. An LLM has not yet been integrated for more flexible, context-aware diagnosis.

These are areas I'd like to improve in future versions.

## Future improvements

There are several things I'd like to work on next:

- Integrate an LLM to improve failure diagnosis and recovery suggestions.
- Run recovery operations inside isolated containers.
- Expand the available recovery actions.
- Improve how failure detection and recovery effectiveness are evaluated.
- Build a dashboard to monitor executions and view their results.
- Add persistent memory so the system can refer to previously encountered failures and solutions.

## Why I built ForgeGuard

I wanted to understand what goes into building an agent system beyond simply connecting an LLM to a set of tools.

While working on ForgeGuard, I got to explore how different components of an agent harness work together, particularly failure diagnosis, recovery planning, tool permissions, controlled execution, verification, and execution tracking.

It also gave me a chance to put these concepts into practice through an actual Python project rather than just studying them individually.

**ForgeGuard is still a prototype, but it provides a starting point for exploring how software engineering agents can become more reliable, controlled, and useful.**
