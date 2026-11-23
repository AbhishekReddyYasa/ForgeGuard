\# ForgeGuard Architecture



\## 1. Overview



ForgeGuard is organised into separate modules, with each module responsible for a specific part of the software reliability workflow.



The main workflow takes a software failure, analyses it, prepares a recovery proposal, checks the required permissions, and executes an approved action.



The architecture is designed to keep diagnosis, recovery planning, execution, verification, and logging separate. This makes the system easier to test, maintain, and extend.



\## 2. High-Level Architecture



```text

&#x20;                FORGEGUARD

&#x20;                     |

&#x20;         +-----------+-----------+

&#x20;         |                       |

&#x20;         v                       v

&#x20;    Agent Layer              Harness Layer

&#x20;         |                       |

&#x20;         v                       v

&#x20;   Failure Diagnoser       Verification Runner

&#x20;         |                       |

&#x20;         v                       v

&#x20;   Diagnosis Coordinator   Security Controls

&#x20;         |                       |

&#x20;         v                       v

&#x20;   Recovery Planner        Controlled Executor

&#x20;         |                       |

&#x20;         +-----------+-----------+

&#x20;                     |

&#x20;                     v

&#x20;             Execution Logger

&#x20;                     |

&#x20;                     v

&#x20;            Execution History

```



\## 3. Main Components



\### 3.1 Agent Layer



The agent layer contains the logic responsible for understanding failures and deciding what recovery action should be proposed.



\*\*Failure Diagnoser\*\*



\- Examines error output.

\- Identifies recognised failure patterns.

\- Classifies failures into categories such as test failure, lint failure, formatting failure, timeout, and execution error.

\- Provides a suggested next step.



\*\*Diagnosis Coordinator\*\*



\- Retrieves failed execution records.

\- Sends failure output to the diagnoser.

\- Collects diagnosis results.

\- Generates a summary of detected failure categories.



\*\*Recovery Planner\*\*



\- Takes the diagnosis result.

\- Selects a predefined recovery action.

\- Describes the proposed action and its risk level.

\- Determines whether approval is required.



\*\*Recovery Coordinator\*\*



\- Connects diagnosis and recovery planning.

\- Passes recovery proposals through the approval gate.

\- Checks whether execution is permitted.

\- Sends permitted actions to the controlled executor.

\- Updates the proposal with the execution result.



\### 3.2 Verification Layer



The verification layer checks whether the project is working correctly.



The verification runner supports predefined command profiles:



| Profile | Purpose |

|---|---|

| `python\_tests` | Runs the Python test suite |

| `ruff\_lint` | Checks code quality |

| `ruff\_format\_check` | Checks code formatting |



Each verification result contains the check name, result, execution duration, and command output.



\### 3.3 Security Layer



The security layer controls which operations can be executed.



\*\*Action Registry\*\*



Maintains a predefined list of available actions and their properties.



\*\*Approval Gate\*\*



Checks whether a recovery action requires approval and whether the required approval has been recorded.



\*\*Controlled Executor\*\*



\- Rejects actions that are not registered.

\- Checks approval requirements.

\- Validates file targets for formatting operations.

\- Uses predefined commands.

\- Applies execution timeouts.

\- Records execution results.



These controls provide application-level safeguards. They do not create a full operating-system sandbox.



\### 3.4 Observability Layer



The observability layer keeps a record of system activity.



\*\*Execution Logger\*\*



Stores execution information in JSON Lines format. Each record includes:



\- Timestamp

\- Check or action name

\- Success or failure status

\- Execution duration

\- Output



\*\*Execution History\*\*



Reads stored records and supports:



\- Viewing previous executions.

\- Filtering records by check name.

\- Filtering successful and failed executions.

\- Calculating execution statistics.



\## 4. Recovery Workflow



The following steps describe how ForgeGuard handles a failure.



1\. \*\*Failure input:\*\* The system receives error output from a failed operation.

2\. \*\*Diagnosis:\*\* The Failure Diagnoser analyses the output and identifies a likely failure category.

3\. \*\*Planning:\*\* The Recovery Planner selects a predefined action based on the diagnosis.

4\. \*\*Approval:\*\* The Approval Gate checks whether the action is allowed to proceed.

5\. \*\*Execution:\*\* The Controlled Executor runs the registered action.

6\. \*\*Verification:\*\* The relevant checks run to assess the result.

7\. \*\*Logging:\*\* Execution details are recorded for future inspection.



```text

Failure

&#x20;  |

&#x20;  v

Diagnose the issue

&#x20;  |

&#x20;  v

Create recovery plan

&#x20;  |

&#x20;  v

Approval required?

&#x20;  |

&#x20;  +---- No ----> Check execution conditions

&#x20;  |

&#x20;  +---- Yes ---> Wait for approval

&#x20;                      |

&#x20;                      v

&#x20;               Approval granted?

&#x20;                      |

&#x20;                +-----+-----+

&#x20;                |           |

&#x20;               Yes          No

&#x20;                |           |

&#x20;                v           v

&#x20;             Execute      Reject

&#x20;                |

&#x20;                v

&#x20;            Log result

&#x20;                |

&#x20;                v

&#x20;          Review history

```



\## 5. Project Directory Structure



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

│   │   ├── result.py

│   │   └── runner.py

│   ├── security/

│   │   ├── action\_registry.py

│   │   ├── approval\_gate.py

│   │   └── controlled\_executor.py

│   └── observability/

│       ├── execution\_logger.py

│       └── execution\_history.py

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

├── README.md

├── requirements.txt

└── pyproject.toml

```



\## 6. Safety Considerations



ForgeGuard uses several safeguards when executing operations:



\- Only registered actions can be executed.

\- File-modifying operations require approval.

\- Formatting targets are checked against the configured workspace.

\- Subprocess execution uses `shell=False`.

\- Execution timeouts help prevent commands from running indefinitely.

\- Execution records make operations traceable.



There are some limitations in the current implementation:



\- The workspace directory is not a complete security sandbox.

\- Subprocesses run with the permissions of the current operating-system user.

\- The approval gate is an application-level control, not an authentication system.

\- Failure diagnosis currently uses predefined error patterns.



\## 7. Current Implementation Status



The current prototype implements the core diagnosis, planning, approval, execution, verification, and logging workflow.



The demonstration simulates a test failure, identifies it, creates a recovery proposal, and reruns the test suite through the controlled executor.



It demonstrates controlled recovery and verification, rather than automatically repairing faulty source code.



\## 8. Future Improvements



Possible improvements include:



\- Integrating an LLM for more flexible failure diagnosis.

\- Adding isolated execution environments.

\- Supporting additional recovery actions.

\- Improving failure classification.

\- Adding a dashboard for execution monitoring.

\- Introducing persistent memory for previous failures and successful recovery strategies.



\---



\*\*ForgeGuard is a prototype for exploring how software engineering agents can perform useful recovery tasks while keeping execution controlled and observable.\*\*

