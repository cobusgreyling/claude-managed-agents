# Security Audit Report — Agent SDK Output

> This is representative output from running `python audit_agent.py ../../sample_target/app.py`.
> Actual output may vary between runs.

```
Starting audit with Agent SDK...
============================================================
  [Tool call: read_file({"path": "../../sample_target/app.py"})]
```

---

## Executive Summary

**Overall Risk Rating: CRITICAL**

The audited Flask application contains multiple severe security vulnerabilities that would allow an attacker to fully compromise the system. Seven distinct findings were identified across four severity levels, including remote code execution, SQL injection, and complete absence of authentication on administrative endpoints.

## Critical Findings

### 1. Remote Code Execution via `eval()`
- **Severity:** Critical
- **Location:** `app.py:admin_run` (line 131-132)
- **Issue:** The `/admin/run` endpoint passes user-supplied input directly to Python's `eval()` function with no sanitisation or sandboxing. An attacker can execute arbitrary code on the server.
- **Fix:** Remove this endpoint entirely. If dynamic code execution is required, use a sandboxed environment with strict allow-listing.

### 2. SQL Injection (Multiple Locations)
- **Severity:** Critical
- **Location:** `app.py:register` (line 59-60), `app.py:login` (line 76-77), `app.py:list_notes` (line 93)
- **Issue:** SQL queries are constructed using f-string interpolation with user input, allowing attackers to inject arbitrary SQL.
- **Fix:** Use parameterised queries with `?` placeholders throughout:
  ```python
  db.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
             (username, password_hash, email))
  ```

### 3. Server-Side Template Injection / XSS
- **Severity:** Critical
- **Location:** `app.py:profile` (line 140-142)
- **Issue:** User-supplied `username` is injected directly into a Jinja2 template via `render_template_string()`. This enables both XSS and server-side template injection (SSTI).
- **Fix:** Use `render_template()` with a static template file and pass `username` as a context variable.

## High Findings

### 4. Weak Password Hashing (MD5)
- **Severity:** High
- **Location:** `app.py:register` (line 55), `app.py:login` (line 72)
- **Issue:** Passwords are hashed with MD5, which is fast and unsalted — trivially crackable with rainbow tables.
- **Fix:** Use `bcrypt` or `argon2` with per-user salts.

### 5. Missing Authentication on Admin Endpoints
- **Severity:** High
- **Location:** `app.py:admin_users` (line 120-125), `app.py:admin_run` (line 128-132)
- **Issue:** Administrative endpoints have no authentication or authorisation checks. Anyone can list all users or execute code.
- **Fix:** Add authentication middleware and role-based access control.

## Medium Findings

### 6. Environment Variable Exposure
- **Severity:** Medium
- **Location:** `app.py:config` (line 148-150)
- **Issue:** The `/config` endpoint returns the entire `os.environ` as JSON, exposing secrets, API keys, and internal configuration.
- **Fix:** Remove this endpoint or restrict it to specific non-sensitive values behind authentication.

### 7. Debug Mode and Insecure Defaults
- **Severity:** Medium
- **Location:** `app.py:__main__` (line 156)
- **Issue:** `debug=True` exposes the Werkzeug debugger (which includes an interactive console) and `host="0.0.0.0"` binds to all interfaces.
- **Fix:** Disable debug mode in production. Bind to `127.0.0.1` or use a reverse proxy.

## Recommendations (Prioritised)

1. **Immediately** remove the `/admin/run` eval endpoint
2. **Immediately** replace all f-string SQL with parameterised queries
3. **Immediately** add authentication to all admin and sensitive endpoints
4. Replace MD5 with bcrypt/argon2 for password hashing
5. Fix template rendering to prevent SSTI/XSS
6. Remove or secure the `/config` endpoint
7. Disable debug mode and restrict host binding
