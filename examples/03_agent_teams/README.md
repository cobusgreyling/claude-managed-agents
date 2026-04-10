# Approach 3: Agent Teams

**Abstraction:** Conversational (Natural Language)
**You own the runtime:** Partially
**Lines of code:** ~70

## What This Demonstrates

Multiple specialised agents collaborate on the same task, each bringing domain expertise:

| Agent | Focus |
|-------|-------|
| **Vulnerability Hunter** | Offensive security — SQLi, XSS, RCE |
| **Auth Reviewer** | Authentication, authorisation, sessions |
| **Best Practices Reviewer** | Code quality, config, deployment |
| **Report Writer** | Synthesises findings into a structured report |

The team self-organises: agents discuss, challenge each other's findings, and the Report Writer compiles everything into a final deliverable.

## Run It

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python team_audit.py ../../sample_target/app.py
```

## Trade-offs

| Pros | Cons |
|------|------|
| Multiple perspectives on the same code | Less predictable output structure |
| Agents challenge each other's findings | Higher token usage (multi-turn) |
| Great for exploratory analysis | You still manage the runtime |
| Natural language role definitions | Harder to integrate into CI/CD |
| Rich, nuanced analysis | Non-deterministic collaboration flow |
