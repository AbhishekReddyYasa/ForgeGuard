

\# ForgeGuard - Project Specification



\## 1. Project Overview



ForgeGuard is an autonomous software reliability

engineering framework designed to help AI agents

perform software maintenance tasks reliably.



It combines agent orchestration, controlled tools,

automated verification, security guardrails,

persistent memory and execution observability.



\## 2. Problem Statement



AI coding agents can generate plausible code while

introducing bugs, breaking existing functionality,

repeating failed actions or accessing resources

outside their intended scope.



ForgeGuard aims to address these problems through

an engineered execution environment.



\## 3. Primary Objectives



1\. Understand software maintenance tasks.

2\. Inspect source code and project instructions.

3\. Plan and execute controlled modifications.

4\. Verify changes using automated checks.

5\. Detect and recover from execution failures.

6\. Enforce explicit tool permissions.

7\. Maintain persistent execution history.

8\. Produce auditable execution reports.



\## 4. Core Components



\- System of Record

\- Agent Orchestrator

\- Tool Execution Engine

\- Verification Engine

\- Security and Permissions Engine

\- Memory and State Management

\- Observability and Reporting



\## 5. Initial Workflow



1\. Receive a maintenance task.

2\. Inspect the target repository.

3\. Read project instructions.

4\. Generate an execution plan.

5\. Execute permitted operations.

6\. Run verification checks.

7\. Analyse failures.

8\. Attempt bounded recovery.

9\. Generate an execution report.



\## 6. Safety Requirements



\- Never expose API keys or secrets.

\- Restrict file operations to the assigned workspace.

\- Require approval for consequential operations.

\- Do not execute unrestricted shell commands.

\- Preserve original test cases.

\- Never modify tests simply to obtain a passing result.

\- Record tool calls and execution outcomes.



\## 7. Evaluation



ForgeGuard will be evaluated against a baseline

tool-using agent using repeatable software

maintenance tasks.



Evaluation metrics include:



\- Task completion rate

\- Test pass rate

\- Regression rate

\- Failure recovery rate

\- Unsafe action blocking rate

\- Tool usage

\- Execution time

\- Human intervention rate



\## 8. Project Constraints



\- Python-based implementation.

\- Configurable LLM provider.

\- Local development environment.

\- Controlled execution workspace.

\- Reproducible evaluation tasks.



\## 9. Definition of Done



The project is complete when the harness can

execute its supported workflow repeatedly,

verify its changes, recover from supported

failures, enforce permissions and produce

reconstructable execution reports.



