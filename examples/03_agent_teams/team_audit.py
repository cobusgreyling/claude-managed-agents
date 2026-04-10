"""
Approach 3: Agent Teams — Conversational multi-agent collaboration.

Multiple specialised agents collaborate on the audit, each contributing
their domain expertise. The team self-organises around the task.

Requirements:
    pip install anthropic claude-agent-sdk

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python team_audit.py ../../sample_target/app.py
"""

import sys
import time
from pathlib import Path
from typing import Any

from anthropic import APIError, APITimeoutError
from claude_agent_sdk import Agent, AgentTeam

MAX_RETRIES: int = 3
RETRY_BASE_DELAY: float = 1.0


def run_team_audit(target_path: str) -> str:
    """
    Spawn a team of specialised agents that collaborate on the audit.
    Each agent has a distinct role and perspective.
    """
    path: Path = Path(target_path)
    if not path.exists():
        print(f"Error: File not found: {path}")
        sys.exit(1)

    code: str = path.read_text()

    # Define specialised agents
    vuln_hunter: Agent = Agent(
        name="Vulnerability Hunter",
        role="""You are an offensive security specialist. Your job is to find
        exploitable vulnerabilities: SQL injection, XSS, RCE, SSRF, path
        traversal, and similar attack vectors. For each finding, describe
        how an attacker would exploit it and rate the severity.""",
    )

    auth_reviewer: Agent = Agent(
        name="Auth Reviewer",
        role="""You are an authentication and authorisation specialist. Review
        all auth flows, session management, password handling, and access
        controls. Flag missing checks, weak algorithms, and privilege
        escalation paths.""",
    )

    best_practices: Agent = Agent(
        name="Best Practices Reviewer",
        role="""You are a Python/Flask best-practices expert. Review code
        quality, configuration safety, error handling, and deployment
        concerns. Flag debug modes, exposed config, missing input
        validation, and dependency issues.""",
    )

    report_writer: Agent = Agent(
        name="Report Writer",
        role="""You are a technical writer who synthesises security findings
        into a clear, actionable audit report. Combine inputs from other
        reviewers into a structured Markdown report with an executive
        summary, categorised findings, severity ratings, and prioritised
        recommendations.""",
    )

    # Create the team
    team: AgentTeam = AgentTeam(
        agents=[vuln_hunter, auth_reviewer, best_practices, report_writer],
        model="claude-sonnet-4-6",
    )

    # Let the team collaborate on the audit
    agents: list[Agent] = [vuln_hunter, auth_reviewer, best_practices, report_writer]
    print("Assembling agent team...")
    for agent in agents:
        print(f"  - {agent.name}")
    print("=" * 60)

    task: str = f"""Perform a comprehensive security audit of the following
    Python Flask application. Each specialist should review from their
    perspective, then the Report Writer should compile everything into
    a single structured report.

    Source code:
    ```python
    {code}
    ```"""

    for attempt in range(MAX_RETRIES):
        try:
            result: Any = team.run(task=task)
            return result.final_output
        except APITimeoutError:
            if attempt < MAX_RETRIES - 1:
                delay: float = RETRY_BASE_DELAY * (2**attempt)
                print(f"  [Timeout, retrying in {delay:.0f}s...]")
                time.sleep(delay)
            else:
                print("  [Error: API timeout after all retries]")
                return "Audit could not be completed: API timeout."
        except APIError as e:
            if e.status_code and e.status_code >= 500 and attempt < MAX_RETRIES - 1:
                delay = RETRY_BASE_DELAY * (2**attempt)
                print(f"  [Server error {e.status_code}, retrying in {delay:.0f}s...]")
                time.sleep(delay)
            else:
                print(f"  [Error: {e}]")
                return f"Audit could not be completed: {e}"

    return "Audit could not be completed: no response from API."


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python team_audit.py <path-to-file>")
        sys.exit(1)

    target: str = sys.argv[1]
    report: str = run_team_audit(target)

    print("\n" + "=" * 60)
    print("TEAM AUDIT REPORT")
    print("=" * 60)
    print(report)

    output_path = Path("team_audit_report.md")
    output_path.write_text(report)
    print(f"\nReport saved to {output_path}")


if __name__ == "__main__":
    main()
