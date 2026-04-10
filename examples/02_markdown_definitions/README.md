# Approach 2: Markdown Agent Definitions

**Abstraction:** Declarative (YAML/MD)
**You own the runtime:** Yes
**Lines of code:** ~50 lines of Markdown (zero Python)

## What This Demonstrates

The agent is defined entirely in a Markdown file with YAML frontmatter. No Python orchestration code. No tool schemas. No agent loop.

The frontmatter declares:
- Which model to use
- Which tools the agent can access
- The agent's identity and instructions

The Markdown body contains the system prompt, process steps, and output format.

## The Agent Definition

See [`security-auditor.md`](security-auditor.md) — that single file *is* the entire agent.

## Run It

This agent definition is designed for use with Claude Code's agent definition system:

```bash
# Place the .md file in your .claude/agents/ directory
cp security-auditor.md ~/.claude/agents/

# Then invoke it from Claude Code
claude "run the security-auditor agent on ../../sample_target/app.py"
```

## Trade-offs

| Pros | Cons |
|------|------|
| Zero Python code to maintain | You still own the runtime (Claude Code) |
| Version-controlled in your repo | Less flexibility than the SDK |
| Easy for non-developers to modify | Tools limited to what the runtime provides |
| Portable across teams | Cannot add custom tool implementations |
| Self-documenting | Debugging is less direct |
