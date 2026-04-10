# Four Ways to Build AI Agents with Claude

**One task. Four paradigms. See the difference.**


![Four Ways To Build AI Agents with Anthropic](blog/images/four-paradigms.png)

This repository accompanies the blog post [Claude Managed Agents: The Fourth Way to Build AI Agents With Claude](blog/claude-managed-agents.md). It implements the **same task** — a security audit of a Python Flask application — using all four of Anthropic's agent paradigms.

The goal: make the trade-offs between paradigms tangible by showing real code side by side.

---

## The Task

All four examples audit [`sample_target/app.py`](sample_target/app.py) — a deliberately vulnerable Flask app with SQL injection, XSS, RCE, weak password hashing, missing auth checks, and exposed configuration.

---

## The Four Approaches

| # | Approach | Code | You Own the Runtime? | Key File | Sample Output |
|---|----------|------|---------------------|----------|---------------|
| 1 | [**Agent SDK**](examples/01_agent_sdk/) | ~120 lines Python | Yes | [`audit_agent.py`](examples/01_agent_sdk/audit_agent.py) | [View](examples/01_agent_sdk/sample_output.md) |
| 2 | [**Markdown Definitions**](examples/02_markdown_definitions/) | ~50 lines Markdown | Yes | [`security-auditor.md`](examples/02_markdown_definitions/security-auditor.md) | [View](examples/02_markdown_definitions/sample_output.md) |
| 3 | [**Agent Teams**](examples/03_agent_teams/) | ~70 lines Python | Partially | [`team_audit.py`](examples/03_agent_teams/team_audit.py) | [View](examples/03_agent_teams/sample_output.md) |
| 4 | [**Managed Agents**](examples/04_managed_agents/) | ~30 lines Python | No | [`audit_agent.py`](examples/04_managed_agents/audit_agent.py) | [View](examples/04_managed_agents/sample_output.md) |

### The Pattern

```
Agent SDK          → You build the kitchen, cook the meal
Markdown Defs      → You write the recipe, hand it to your team
Agent Teams        → You describe what you want, a group figures it out
Managed Agents     → You order from a restaurant
```

---

## Quick Start

### Run everything at once

```bash
export ANTHROPIC_API_KEY=sk-ant-...
make install    # Install all dependencies
make run-all    # Run approaches 1, 3, and 4 sequentially
```

### Run individually

```bash
# Set your API key
export ANTHROPIC_API_KEY=sk-ant-...

# Approach 1: Agent SDK
cd examples/01_agent_sdk
pip install -r requirements.txt
python audit_agent.py ../../sample_target/app.py

# Approach 2: Markdown Definitions
# Copy to your Claude Code agents directory and invoke
cp examples/02_markdown_definitions/security-auditor.md ~/.claude/agents/

# Approach 3: Agent Teams
cd examples/03_agent_teams
pip install -r requirements.txt
python team_audit.py ../../sample_target/app.py

# Approach 4: Managed Agents
cd examples/04_managed_agents
pip install -r requirements.txt
python audit_agent.py ../../sample_target/app.py
```

---

## What You'll Notice

1. **Code volume drops dramatically** from Approach 1 to 4
2. **Control decreases** in the same direction — that's the trade-off
3. **Infrastructure responsibility shifts** from you to Anthropic
4. **The audit output is comparable** across all four — the *what* stays the same, only the *how* changes

---

## Cost & Latency Comparison

Approximate figures from auditing `sample_target/app.py` (157 lines). Costs based on Claude Sonnet 4.6 pricing ($3/MTok input, $15/MTok output).

| Approach | Input Tokens | Output Tokens | Est. Cost | Latency | Notes |
|----------|-------------|---------------|-----------|---------|-------|
| Agent SDK | ~8K | ~4K | ~$0.08 | ~8s | 2-3 tool call rounds |
| Markdown Definitions | ~6K | ~4K | ~$0.08 | ~10s | Runs inside Claude Code |
| Agent Teams | ~35K | ~15K | ~$0.33 | ~30s | 4 agents × multi-turn |
| Managed Agents | ~8K | ~4K | ~$0.08 + session | ~12s | + $0.08/session-hour |

**Key takeaway:** Approaches 1, 2, and 4 have similar token costs for single-file audits. Agent Teams (Approach 3) uses significantly more tokens due to multi-agent conversation overhead but produces richer, multi-perspective analysis.

---

## Architecture Comparison

![Four Ways To Build AI Agents with Anthropic](blog/images/four-paradigms.png)

---

## The Blog

The full blog post with architecture diagrams, pricing details, and strategic analysis is in [`blog/claude-managed-agents.md`](blog/claude-managed-agents.md).

---

## Prerequisites

- Python 3.10+
- An [Anthropic API key](https://console.anthropic.com/)
- `pip install anthropic` (all approaches)
- `pip install claude-agent-sdk` (Approach 3 only)

---

## License

MIT
