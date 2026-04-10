# Security Audit Report — Agent Teams Output

> This is representative output from running `python team_audit.py ../../sample_target/app.py`.
> Actual output may vary between runs. The multi-agent format produces richer, more nuanced analysis.

```
Assembling agent team...
  - Vulnerability Hunter
  - Auth Reviewer
  - Best Practices Reviewer
  - Report Writer
============================================================
```

---

# Security Audit Report

## Executive Summary

**Overall Risk Rating: CRITICAL**

A team of four specialised agents — vulnerability hunting, authentication review, best practices, and report synthesis — independently assessed this Flask application. All reviewers converged on the same conclusion: the application is not safe for production deployment.

**Key Statistics:**
- 3 Critical vulnerabilities
- 2 High-severity issues
- 2 Medium-severity issues
- 0 Low-severity issues

The most dangerous finding is an unrestricted `eval()` endpoint that grants full remote code execution to any unauthenticated user.

---

## Critical Findings

### 1. Remote Code Execution via `eval()`

*Identified by: Vulnerability Hunter*

- **Severity:** Critical
- **Location:** `app.py:admin_run` (lines 128-132)
- **Attack Vector:** `POST /admin/run` with `{"code": "__import__('os').system('rm -rf /')"}`
- **Issue:** The endpoint passes user input directly to Python's `eval()` with no authentication, input validation, or sandboxing. An attacker gains full control of the server.
- **Fix:** Remove this endpoint entirely. No amount of sanitisation makes `eval()` safe with untrusted input.

### 2. SQL Injection at Three Endpoints

*Identified by: Vulnerability Hunter, confirmed by Auth Reviewer*

- **Severity:** Critical
- **Location:** `app.py:register` (line 60), `app.py:login` (line 77), `app.py:list_notes` (line 93)
- **Attack Vector:** `POST /login` with `{"username": "' OR '1'='1", "password": "anything"}`
- **Issue:** All three endpoints use f-string formatting to build SQL queries, allowing injection of arbitrary SQL. The login bypass is particularly dangerous as it grants access without valid credentials.
- **Fix:** Use parameterised queries:
  ```python
  db.execute("SELECT * FROM users WHERE username=? AND password=?",
             (username, password_hash))
  ```

### 3. Server-Side Template Injection

*Identified by: Vulnerability Hunter*

- **Severity:** Critical
- **Location:** `app.py:profile` (lines 138-142)
- **Attack Vector:** `GET /profile/{{7*7}}` returns "Profile: 49", confirming SSTI. Escalates to RCE via Jinja2's sandbox escape.
- **Issue:** `render_template_string()` with user-controlled input allows server-side template injection, which chains to remote code execution in Jinja2.
- **Fix:** Use `render_template()` with a pre-defined template file.

---

## High Findings

### 4. Weak Password Hashing (MD5, Unsalted)

*Identified by: Auth Reviewer*

- **Severity:** High
- **Location:** `app.py:register` (line 55), `app.py:login` (line 72)
- **Issue:** Passwords are hashed with `hashlib.md5()` — a fast, unsalted hash. MD5 is not a password hashing algorithm. A modern GPU can compute billions of MD5 hashes per second, and rainbow tables for common passwords are freely available.
- **Fix:** Use `bcrypt` (via the `bcrypt` package) or `argon2id` (via `argon2-cffi`). Both handle salting automatically.

### 5. Missing Authentication and Authorisation

*Identified by: Auth Reviewer*

- **Severity:** High
- **Location:** `app.py:admin_users` (line 120), `app.py:admin_run` (line 128), `app.py:delete_note` (line 109), `app.py:list_notes` (line 88)
- **Issue:** No authentication mechanism exists anywhere in the application. Admin endpoints are fully public. The notes endpoints allow any user to read or delete any other user's notes by manipulating `user_id` or `note_id`.
- **Fix:** Implement session-based or token-based authentication. Add role-based access control for admin routes. Enforce ownership checks on note operations.

---

## Medium Findings

### 6. Environment Variable Disclosure

*Identified by: Best Practices Reviewer*

- **Severity:** Medium
- **Location:** `app.py:config` (lines 147-150)
- **Issue:** The `/config` endpoint returns `dict(os.environ)` as JSON, exposing database paths, API keys, cloud credentials, and any other secrets stored in environment variables.
- **Fix:** Remove this endpoint. If configuration introspection is needed, expose only specific allow-listed values behind authentication.

### 7. Debug Mode and Network Exposure

*Identified by: Best Practices Reviewer*

- **Severity:** Medium
- **Location:** `app.py:__main__` (line 156)
- **Issue:** `debug=True` enables the Werkzeug interactive debugger, which provides a Python REPL on error pages (another RCE vector). `host="0.0.0.0"` binds to all network interfaces, making the app accessible from any network.
- **Fix:** Set `debug=False` in production. Use a WSGI server (gunicorn, uvicorn) behind a reverse proxy. Bind to `127.0.0.1` unless explicitly needed.

---

## Recommendations (Prioritised)

1. **Immediate:** Remove the `/admin/run` eval endpoint — this is an open backdoor
2. **Immediate:** Replace all f-string SQL with parameterised queries
3. **Immediate:** Add authentication to all endpoints; add authorisation to admin and sensitive routes
4. **Short-term:** Replace MD5 with bcrypt/argon2 for password hashing
5. **Short-term:** Fix template rendering to use static templates
6. **Short-term:** Remove or restrict the `/config` endpoint
7. **Before deployment:** Disable debug mode, use a production WSGI server, restrict network binding

---

*Report compiled by Report Writer from findings by Vulnerability Hunter, Auth Reviewer, and Best Practices Reviewer.*
