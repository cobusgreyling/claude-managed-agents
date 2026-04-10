# Approach 4: Managed Agents

**Abstraction:** Hosted service (API)
**You own the runtime:** No
**Lines of code:** ~30

## What This Demonstrates

The entire agent — orchestration, tool execution, sandboxing, state management, and error recovery — is handled by Anthropic. You write four API calls:

1. **Create an agent** — define the model, system prompt, and toolset
2. **Create an environment** — configure the sandbox
3. **Start a session** — tie agent to environment
4. **Stream events** — send the task and receive results

That's it. No agent loop. No tool schemas. No tool handlers. No state management. No error recovery code.

## Run It

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python audit_agent.py
```

## The Key Difference

Compare the code in this directory (~30 lines) to:
- **Agent SDK** (~120 lines) — you write the loop, tools, and handlers
- **Markdown Definitions** (~50 lines of MD) — you own the runtime
- **Agent Teams** (~70 lines) — you manage agent coordination

Managed Agents collapses all of that into API calls. The sandbox runs in Anthropic's cloud. The agent has access to bash, file operations, web search, and more — without you implementing any of it.

## Trade-offs

| Pros | Cons |
|------|------|
| Minimal code | No custom tool implementations |
| Zero infrastructure to manage | Code runs in Anthropic's cloud, not yours |
| Built-in sandboxing and security | Less control over execution environment |
| Persistent sessions across interactions | Vendor dependency |
| Automatic error recovery | Runtime costs ($0.08/session-hour) |
| Mid-execution steering | Beta API — subject to change |
