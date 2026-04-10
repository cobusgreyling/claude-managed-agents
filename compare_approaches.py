"""
Compare all four agent paradigms side by side.

Runs Approaches 1, 3, and 4 against the sample target and produces a
summary table with token usage, timing, and vulnerability counts.

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python compare_approaches.py
"""

import re
import subprocess
import sys
import time
from pathlib import Path

TARGET = "sample_target/app.py"

APPROACHES = [
    {
        "name": "Agent SDK",
        "dir": "examples/01_agent_sdk",
        "cmd": ["python", "audit_agent.py", f"../../{TARGET}"],
        "report": "examples/01_agent_sdk/audit_report.md",
    },
    {
        "name": "Agent Teams",
        "dir": "examples/03_agent_teams",
        "cmd": ["python", "team_audit.py", f"../../{TARGET}"],
        "report": "examples/03_agent_teams/team_audit_report.md",
    },
    {
        "name": "Managed Agents",
        "dir": "examples/04_managed_agents",
        "cmd": ["python", "audit_agent.py", f"../../{TARGET}"],
        "report": "examples/04_managed_agents/audit_report.md",
    },
]

SEVERITY_KEYWORDS = ["critical", "high", "medium", "low"]


def count_findings(report_path: str) -> dict[str, int]:
    """Count severity mentions in a report file."""
    text = Path(report_path).read_text().lower()
    counts: dict[str, int] = {}
    for severity in SEVERITY_KEYWORDS:
        counts[severity] = len(re.findall(rf"\b{severity}\b", text))
    return counts


def run_approach(approach: dict) -> dict:
    """Run a single approach and collect metrics."""
    print(f"\n{'='*60}")
    print(f"Running: {approach['name']}")
    print(f"{'='*60}")

    start: float = time.time()
    result = subprocess.run(
        approach["cmd"],
        cwd=approach["dir"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    elapsed: float = time.time() - start

    success: bool = result.returncode == 0
    findings: dict[str, int] = {}
    report_lines: int = 0

    if success and Path(approach["report"]).exists():
        findings = count_findings(approach["report"])
        report_lines = len(Path(approach["report"]).read_text().splitlines())

    return {
        "name": approach["name"],
        "success": success,
        "elapsed": elapsed,
        "findings": findings,
        "report_lines": report_lines,
        "stderr": result.stderr.strip() if not success else "",
    }


def print_table(results: list[dict]) -> None:
    """Print a comparison table."""
    print(f"\n{'='*80}")
    print("COMPARISON RESULTS")
    print(f"{'='*80}")
    print(
        f"{'Approach':<20} {'Status':<10} {'Time':>8} {'Lines':>7} "
        f"{'Crit':>6} {'High':>6} {'Med':>6} {'Low':>6}"
    )
    print("-" * 80)

    for r in results:
        status: str = "OK" if r["success"] else "FAIL"
        elapsed: str = f"{r['elapsed']:.1f}s"
        lines: str = str(r["report_lines"]) if r["success"] else "-"
        f = r["findings"]
        crit: str = str(f.get("critical", 0)) if r["success"] else "-"
        high: str = str(f.get("high", 0)) if r["success"] else "-"
        med: str = str(f.get("medium", 0)) if r["success"] else "-"
        low: str = str(f.get("low", 0)) if r["success"] else "-"

        print(
            f"{r['name']:<20} {status:<10} {elapsed:>8} {lines:>7} "
            f"{crit:>6} {high:>6} {med:>6} {low:>6}"
        )

        if not r["success"] and r["stderr"]:
            print(f"  Error: {r['stderr'][:200]}")

    print("-" * 80)
    print("Note: Finding counts are keyword frequency, not deduplicated findings.")
    print("Approach 2 (Markdown Definitions) runs inside Claude Code and is not included.\n")


def main() -> None:
    if not Path(TARGET).exists():
        print(f"Error: Target file not found: {TARGET}")
        print("Run this script from the repository root.")
        sys.exit(1)

    results: list[dict] = []
    for approach in APPROACHES:
        try:
            results.append(run_approach(approach))
        except subprocess.TimeoutExpired:
            results.append({
                "name": approach["name"],
                "success": False,
                "elapsed": 120.0,
                "findings": {},
                "report_lines": 0,
                "stderr": "Timed out after 120s",
            })

    print_table(results)


if __name__ == "__main__":
    main()
