\# ForgeGuard 🛡️



\*\*A Python-based agent harness for diagnosing software failures and managing controlled recovery.\*\*



Software projects don't always behave as expected. Tests fail, formatting gets inconsistent, and figuring out what went wrong can take more time than fixing the actual problem.



I built ForgeGuard to explore how an agent-based system could help with this process. The idea is simple: detect a failure, understand its category, suggest an appropriate recovery action, check whether that action is allowed, and execute it in a controlled way.



The project focuses on making that workflow traceable, testable, and safer rather than allowing an agent to run arbitrary commands.



\## What can it do?



\- \*\*Detect failures:\*\* Recognises common issues such as failed tests, lint errors, formatting problems, and execution timeouts.

\- \*\*Suggest recovery actions:\*\* Creates a recovery plan based on the detected problem.

\- \*\*Check permissions:\*\* Allows read-only actions to proceed while requiring approval for file-modifying actions.

\- \*\*Execute controlled actions:\*\* Runs operations from a predefined list instead of accepting arbitrary commands.

\- \*\*Keep an execution history:\*\* Records what ran, whether it succeeded, how long it took, and its output.

\- \*\*Run verification checks:\*\* Uses pytest and Ruff to check the project's health.



\## How it works



ForgeGuard follows a straightforward workflow:



1\. A software failure is provided to the system.

2\. The failure diagnoser identifies the likely issue.

3\. The recovery planner creates a proposed action.

4\. The approval gate checks whether the action can proceed.

5\. The controlled executor runs the permitted operation.

6\. The result is saved in the execution log.

7\. Execution history can be reviewed to understand previous runs.



```text

&#x20;      Software Failure

&#x20;             |

&#x20;             v

&#x20;      Failure Diagnoser

&#x20;             |

&#x20;             v

&#x20;       Recovery Planner

&#x20;             |

&#x20;             v

&#x20;        Approval Gate

&#x20;             |

&#x20;             v

&#x20;     Controlled Executor

&#x20;             |

&#x20;             v

&#x20;      Verification Checks

&#x20;             |

&#x20;             v

&#x20;      Execution Logger

&#x20;             |

&#x20;             v

&#x20;      Execution History

```



\## Available recovery actions



The executor currently supports three predefined actions:



| Action | What it does | Approval |

|---|---|---|

| `run\_python\_tests` | Runs the project's test suite | Not required |

| `run\_ruff\_lint` | Checks the code for linting issues | Not required |

| `format\_python\_file` | Formats a selected Python file | Required |



The action registry controls which operations are available. Unknown actions are rejected.



\## Built with



\- Python 3.13

\- Pytest for testing

\- Ruff for linting and formatting

\- SQLAlchemy, Pydantic and PyYAML

\- Git for version control



\## Getting started



You'll need Python 3.13 or later and Git installed.



\*\*1. Clone the repository\*\*



```cmd

git clone <repository-url>

cd ForgeGuard

```



\*\*2. Create and activate a virtual environment\*\*



```cmd

python -m venv .venv

.venv\\Scripts\\activate

```



\*\*3. Install the dependencies\*\*



```cmd

python -m pip install -r requirements.txt

```



\## Running the project



The easiest way to see ForgeGuard in action is to run the demo:



```cmd

python -m scripts.demo

```



The demo simulates a test failure, diagnoses it, generates a recovery plan, checks permissions, and then runs the test suite through the controlled executor. It also displays the execution result and history statistics.



You can run the checks individually too:



\*\*Run tests\*\*

```cmd

python -m pytest -q

```



\*\*Check code quality\*\*

```cmd

python -m ruff check .

```



\*\*Check formatting\*\*

```cmd

python -m ruff format --check .

```



\## Project structure



```text

ForgeGuard/

│

├── agent/

│   ├── core/

│   │   ├── failure\_diagnoser.py

│   │   ├── diagnosis\_coordinator.py

│   │   ├── recovery\_planner.py

│   │   └── recovery\_coordinator.py

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



\## Testing



The latest full test run during development produced the following results:



| Result | Count |

|---|---:|

| Tests collected | 115 |

| Passed | 114 |

| Failed | 0 |

| Skipped | 1 |



The skipped test is related to symbolic-link availability in the Windows environment.



\## A note about safety



One of the main things I wanted to explore with ForgeGuard was how an agent could be given useful tools without giving it unrestricted control over the system.



The current implementation uses:

\- A predefined action registry.

\- Approval checks for file-modifying operations.

\- Workspace path validation for formatting targets.

\- Timeouts for executed operations.

\- `shell=False` when launching subprocesses.

\- Execution logs for traceability.



There are still limitations. The executor runs with the permissions of the current Windows user, so the workspace is not an operating-system sandbox. The approval mechanism is an application-level check, not a secure authentication system. Failure diagnosis currently relies on predefined error patterns rather than an integrated LLM.



These are important areas for further development.



\## What's next?



Some improvements I'd like to explore:



\- Connecting an LLM for more context-aware failure diagnosis.

\- Running recovery operations inside isolated containers.

\- Adding more recovery tools.

\- Improving failure detection and recovery evaluation.

\- Building a dashboard to monitor executions.

\- Introducing persistent memory for previous failures and solutions.



\## Why I built it



This project gave me an opportunity to understand how agent harnesses work beyond simply connecting an LLM to a few tools. It helped me explore tool permissions, execution control, verification loops, recovery workflows, and observability in a practical software project.



\*\*ForgeGuard is a prototype and a foundation for experimenting with safer, more reliable software engineering agents.\*\*

