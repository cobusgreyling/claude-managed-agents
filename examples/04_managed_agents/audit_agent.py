"""
Approach 4: Managed Agents — Anthropic handles everything.

You define WHAT you want. Anthropic handles the HOW:
orchestration, sandboxing, tool execution, state, and recovery.

This is the entire agent. ~30 lines of meaningful code.

Requirements:
    pip install anthropic

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python audit_agent.py
"""

from anthropic import Anthropic

client = Anthropic()

# Step 1: Create the agent (one-time setup, reuse the ID after)
agent = client.beta.agents.create(
    name="Security Auditor",
    model="claude-sonnet-4-6",
    system="""You are a senior security auditor. Analyse any code provided
    and produce a structured audit report covering: critical vulnerabilities,
    authentication flaws, data exposure risks, and best-practice violations.
    Include severity ratings, locations, and recommended fixes.""",
    tools=[{"type": "agent_toolset_20260401"}],
)

# Step 2: Create a sandboxed environment
environment = client.beta.environments.create(
    name="audit-env",
    config={
        "type": "cloud",
        "networking": {"type": "restricted"},
    },
)

# Step 3: Start a session
session = client.beta.sessions.create(
    agent=agent.id,
    environment_id=environment.id,
    title="Security Audit",
)

# Step 4: Send the task and stream results
with client.beta.sessions.events.stream(session.id) as stream:
    client.beta.sessions.events.send(
        session.id,
        events=[{
            "type": "user.message",
            "content": [{
                "type": "text",
                "text": """Audit this Flask application for security vulnerabilities:

```python
import os, sqlite3, hashlib
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
DATABASE = os.getenv("DATABASE_PATH", "app.db")

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    password_hash = hashlib.md5(data["password"].encode()).hexdigest()
    db = get_db()
    db.execute(f"INSERT INTO users (username, password, email) VALUES ('{data['username']}', '{password_hash}', '{data.get('email', '')}')")
    db.commit()
    return jsonify({"status": "ok"})

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    password_hash = hashlib.md5(data["password"].encode()).hexdigest()
    db = get_db()
    row = db.execute(f"SELECT * FROM users WHERE username='{data['username']}' AND password='{password_hash}'").fetchone()
    if row:
        return jsonify({"status": "ok", "role": row["role"]})
    return jsonify({"status": "error"}), 401

@app.route("/notes", methods=["GET"])
def list_notes():
    user_id = request.args.get("user_id")
    db = get_db()
    rows = db.execute(f"SELECT * FROM notes WHERE user_id={user_id}").fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/notes/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):
    db = get_db()
    db.execute("DELETE FROM notes WHERE id=?", (note_id,))
    db.commit()
    return jsonify({"status": "deleted"})

@app.route("/admin/users")
def admin_users():
    db = get_db()
    rows = db.execute("SELECT id, username, email, role FROM users").fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/admin/run", methods=["POST"])
def admin_run():
    code = request.get_json().get("code", "")
    result = eval(code)
    return jsonify({"result": str(result)})

@app.route("/profile/<username>")
def profile(username):
    html = f"<h1>Profile: {username}</h1>"
    return render_template_string(html)

@app.route("/config")
def config():
    return jsonify(dict(os.environ))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
```

Produce a full security audit report in Markdown format.""",
            }],
        }],
    )

    for event in stream:
        match event.type:
            case "agent.message":
                for block in event.content:
                    if hasattr(block, "text"):
                        print(block.text, end="")
            case "agent.tool_use":
                print(f"\n  [Tool: {event.name}]")
            case "session.status_idle":
                print("\n\nAudit complete.")
                break
