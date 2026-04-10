# Approach 1: Agent SDK

**Abstraction:** Programmatic (Python)
**You own the runtime:** Yes
**Lines of code:** ~120

## What This Demonstrates

You write the entire agent loop yourself:
- Define tools and their schemas
- Call `client.messages.create()` in a loop
- Check `stop_reason` to detect tool calls vs. final output
- Execute tools locally and feed results back
- Handle errors, retries, and conversation state

This gives you **full control** over every decision the agent makes, at the cost of writing and maintaining all the orchestration code.

## Run It

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python audit_agent.py ../../sample_target/app.py
```

## Trade-offs

| Pros | Cons |
|------|------|
| Full control over the agent loop | You write and maintain all orchestration |
| Custom tool implementations | You handle retries, errors, state |
| Works anywhere Python runs | More code = more surface area for bugs |
| Easy to test and debug | Every new tool needs schema + handler |
