"""
Approach 4: Managed Agents — Anthropic handles everything.

You define WHAT you want. Anthropic handles the HOW:
orchestration, sandboxing, tool execution, state, and recovery.

This is the entire agent. ~30 lines of meaningful code.

Requirements:
    pip install anthropic

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python audit_agent.py ../../sample_target/app.py
"""

import sys
from pathlib import Path

from anthropic import Anthropic, APIError


def run_audit(target_path: str) -> str:
    """Run a managed agent audit on the target file."""
    path = Path(target_path)
    if not path.exists():
        print(f"Error: File not found: {path}")
        sys.exit(1)

    code: str = path.read_text()
    client = Anthropic()

    try:
        # Step 1: Create the agent (one-time setup, reuse the ID after)
        agent = client.beta.agents.create(
            name="Security Auditor",
            model="claude-sonnet-4-6",
            system="""You are a senior security auditor. Analyse any code provided
            and produce a structured audit report covering: critical vulnerabilities,
            authentication flaws, data exposure risks, and best-practice violations.
            Include severity ratings, locations, and recommended fixes.""",
            tools=[{"type": "agent_toolset_20260401"}],
        )

        # Step 2: Create a sandboxed environment
        environment = client.beta.environments.create(
            name="audit-env",
            config={
                "type": "cloud",
                "networking": {"type": "restricted"},
            },
        )

        # Step 3: Start a session
        session = client.beta.sessions.create(
            agent=agent.id,
            environment_id=environment.id,
            title="Security Audit",
        )
    except APIError as e:
        print(f"Error setting up managed agent: {e}")
        return f"Audit could not be completed: {e}"

    # Step 4: Send the task and stream results
    output_parts: list[str] = []

    with client.beta.sessions.events.stream(session.id) as stream:
        client.beta.sessions.events.send(
            session.id,
            events=[{
                "type": "user.message",
                "content": [{
                    "type": "text",
                    "text": (
                        "Audit this Flask application for security "
                        "vulnerabilities:\n\n"
                        f"```python\n{code}\n```\n\n"
                        "Produce a full security audit report in Markdown format."
                    ),
                }],
            }],
        )

        for event in stream:
            match event.type:
                case "agent.message":
                    for block in event.content:
                        if hasattr(block, "text"):
                            print(block.text, end="")
                            output_parts.append(block.text)
                case "agent.tool_use":
                    print(f"\n  [Tool: {event.name}]")
                case "session.status_idle":
                    print("\n\nAudit complete.")
                    break

    return "".join(output_parts)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python audit_agent.py <path-to-file>")
        sys.exit(1)

    target = sys.argv[1]
    report = run_audit(target)

    output_path = Path("audit_report.md")
    output_path.write_text(report)
    print(f"\nReport saved to {output_path}")


if __name__ == "__main__":
    main()
