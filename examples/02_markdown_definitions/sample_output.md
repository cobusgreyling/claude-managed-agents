# Security Audit Report — Markdown Definitions Output

> This is representative output from running the `security-auditor` agent definition in Claude Code.
> Actual output may vary between runs.

```
⏺ Using tools: Glob, Read, Grep, Bash
⏺ Scanning ../../sample_target/ for Python files...
  Found: app.py
⏺ Reading app.py...
⏺ Searching for dangerous patterns...
  ✓ eval( — 1 match (line 132)
  ✓ f"SELECT — 1 match (line 77)
  ✓ f"INSERT — 1 match (line 60)
  ✓ render_template_string — 1 match (line 142)
  ✓ hashlib.md5 — 2 matches (lines 55, 72)
  ✓ debug=True — 1 match (line 156)
  ✓ os.environ — 1 match (line 150)
```

---

# Security Audit Report

## Executive Summary

**Risk Rating: CRITICAL** — 7 findings across 4 severity levels.

The application contains multiple exploitable vulnerabilities including remote code execution, SQL injection at three locations, and server-side template injection. No authentication exists on administrative endpoints. Immediate remediation is required before any production deployment.

## Critical Findings

### Remote Code Execution — `eval()`
- **Severity:** Critical
- **Location:** `app.py:admin_run` (line 132)
- **Issue:** User-supplied code is passed directly to `eval()`, allowing arbitrary Python execution on the server.
- **Fix:** Remove this endpoint. If needed, use a sandboxed execution environment.

### SQL Injection — String-Formatted Queries
- **Severity:** Critical
- **Location:** `app.py:register` (line 60), `app.py:login` (line 77), `app.py:list_notes` (line 93)
- **Issue:** Three endpoints construct SQL using f-strings with unsanitised user input.
- **Fix:** Use parameterised queries (`?` placeholders) for all database operations.

### Server-Side Template Injection
- **Severity:** Critical
- **Location:** `app.py:profile` (line 142)
- **Issue:** `render_template_string()` with user-controlled input enables SSTI and reflected XSS.
- **Fix:** Use `render_template()` with a static template file.

## High Findings

### Weak Password Hashing
- **Severity:** High
- **Location:** `app.py:register` (line 55), `app.py:login` (line 72)
- **Issue:** MD5 is used for password hashing — unsalted, fast, and trivially reversible.
- **Fix:** Use `bcrypt` or `argon2id` with automatic salting.

### Missing Authentication on Admin Endpoints
- **Severity:** High
- **Location:** `app.py:admin_users` (line 121), `app.py:admin_run` (line 129)
- **Issue:** Admin endpoints have no auth checks. Any user (or anonymous request) can access them.
- **Fix:** Add authentication middleware with role-based access control.

## Medium Findings

### Environment Variable Disclosure
- **Severity:** Medium
- **Location:** `app.py:config` (line 150)
- **Issue:** `/config` exposes the full `os.environ` dict, including secrets and API keys.
- **Fix:** Remove this endpoint or restrict to allow-listed keys behind authentication.

### Debug Mode Enabled
- **Severity:** Medium
- **Location:** `app.py:__main__` (line 156)
- **Issue:** `debug=True` exposes the Werkzeug interactive debugger. `host="0.0.0.0"` binds publicly.
- **Fix:** Set `debug=False` in production. Bind to `127.0.0.1`.

## Recommendations

1. Remove the `/admin/run` endpoint immediately
2. Replace all f-string SQL with parameterised queries
3. Add authentication and authorisation to all endpoints
4. Migrate to bcrypt/argon2 for password hashing
5. Use static templates instead of `render_template_string()`
6. Remove `/config` or gate behind auth
7. Disable debug mode for production deployments
