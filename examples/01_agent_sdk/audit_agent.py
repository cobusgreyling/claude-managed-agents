"""
Approach 1: Agent SDK — Full programmatic control.

You own the agent loop. You decide when to call tools, how to handle
responses, and what to do with errors. Maximum flexibility, maximum code.

Requirements:
    pip install anthropic

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python audit_agent.py ../sample_target/app.py
"""

import json
import sys
from pathlib import Path

from anthropic import Anthropic

SYSTEM_PROMPT = """You are a senior security auditor. Analyse the provided source code
and produce a structured audit report covering:

1. **Critical vulnerabilities** (SQL injection, XSS, RCE, etc.)
2. **Authentication & authorisation flaws**
3. **Data exposure risks**
4. **Best-practice violations**

For each finding, include:
- Severity (Critical / High / Medium / Low)
- Location (function name and line reference)
- Description of the issue
- Recommended fix

End with an executive summary and an overall risk rating."""

# Tools the agent can call — we implement them ourselves
TOOLS = [
    {
        "name": "read_file",
        "description": "Read the contents of a file at the given path.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to read.",
                }
            },
            "required": ["path"],
        },
    },
    {
        "name": "list_files",
        "description": "List files in a directory.",
        "input_schema": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "Directory path to list.",
                }
            },
            "required": ["directory"],
        },
    },
]


def handle_tool_call(name: str, input_data: dict) -> str:
    """Execute a tool call and return the result as a string."""
    if name == "read_file":
        path = Path(input_data["path"])
        if not path.exists():
            return f"Error: File not found: {path}"
        return path.read_text()

    elif name == "list_files":
        directory = Path(input_data["directory"])
        if not directory.is_dir():
            return f"Error: Not a directory: {directory}"
        return "\n".join(str(p) for p in sorted(directory.iterdir()))

    return f"Error: Unknown tool: {name}"


def run_audit(target_path: str) -> str:
    """
    Run the full agent loop:
      1. Send the task to Claude with tools available.
      2. If Claude wants to call a tool, execute it and feed results back.
      3. Repeat until Claude produces a final text response.
    """
    client = Anthropic()
    messages = [
        {
            "role": "user",
            "content": f"Please audit the code in this file: {target_path}",
        }
    ]

    print("Starting audit with Agent SDK...")
    print("=" * 60)

    while True:
        # Call Claude
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        # Check if Claude wants to use tools
        if response.stop_reason == "tool_use":
            # Collect all tool uses from this response
            assistant_content = response.content
            tool_results = []

            for block in assistant_content:
                if block.type == "tool_use":
                    print(f"  [Tool call: {block.name}({json.dumps(block.input)})]")
                    result = handle_tool_call(block.name, block.input)
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        }
                    )

            # Feed results back into the conversation
            messages.append({"role": "assistant", "content": assistant_content})
            messages.append({"role": "user", "content": tool_results})

        elif response.stop_reason == "end_turn":
            # Claude is done — extract final text
            final_text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    final_text += block.text
            return final_text

        else:
            print(f"  [Unexpected stop reason: {response.stop_reason}]")
            break

    return "Audit could not be completed."


def main():
    if len(sys.argv) < 2:
        print("Usage: python audit_agent.py <path-to-file>")
        sys.exit(1)

    target = sys.argv[1]
    report = run_audit(target)

    print("\n" + "=" * 60)
    print("AUDIT REPORT")
    print("=" * 60)
    print(report)

    # Save report
    output_path = Path("audit_report.md")
    output_path.write_text(report)
    print(f"\nReport saved to {output_path}")


if __name__ == "__main__":
    main()
