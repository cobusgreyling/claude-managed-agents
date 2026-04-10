"""
Sample Flask application with intentional code quality issues.
This is the target that all four agent paradigms will audit.
"""

import hashlib
import os
import sqlite3

from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)
DATABASE = os.getenv("DATABASE_PATH", "app.db")


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            role TEXT DEFAULT 'user'
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.commit()


# --- Authentication ---


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data["username"]
    password = data["password"]
    email = data.get("email", "")

    # Issue: MD5 for password hashing
    password_hash = hashlib.md5(password.encode()).hexdigest()

    db = get_db()
    # Issue: SQL injection via string formatting
    db.execute(
        f"INSERT INTO users (username, password, email) VALUES "
        f"('{username}', '{password_hash}', '{email}')"
    )
    db.commit()
    return jsonify({"status": "ok", "message": f"User {username} created"})


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data["username"]
    password = data["password"]

    password_hash = hashlib.md5(password.encode()).hexdigest()

    db = get_db()
    # Issue: SQL injection
    row = db.execute(
        f"SELECT * FROM users WHERE username='{username}' AND password='{password_hash}'"
    ).fetchone()

    if row:
        # Issue: no real session/token management
        return jsonify({"status": "ok", "role": row["role"]})
    return jsonify({"status": "error", "message": "Invalid credentials"}), 401


# --- Notes CRUD ---


@app.route("/notes", methods=["GET"])
def list_notes():
    user_id = request.args.get("user_id")
    db = get_db()
    # Issue: SQL injection, no auth check
    rows = db.execute(f"SELECT * FROM notes WHERE user_id={user_id}").fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/notes", methods=["POST"])
def create_note():
    data = request.get_json()
    db = get_db()
    db.execute(
        "INSERT INTO notes (user_id, title, content) VALUES (?, ?, ?)",
        (data["user_id"], data["title"], data["content"]),
    )
    db.commit()
    return jsonify({"status": "ok"})


@app.route("/notes/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):
    db = get_db()
    # Issue: no authorisation check — any user can delete any note
    db.execute("DELETE FROM notes WHERE id=?", (note_id,))
    db.commit()
    return jsonify({"status": "deleted"})


# --- Admin ---


@app.route("/admin/users")
def admin_users():
    # Issue: no auth/role check for admin endpoint
    db = get_db()
    rows = db.execute("SELECT id, username, email, role FROM users").fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/admin/run", methods=["POST"])
def admin_run():
    # Issue: remote code execution
    code = request.get_json().get("code", "")
    result = eval(code)
    return jsonify({"result": str(result)})


# --- Rendering ---


@app.route("/profile/<username>")
def profile(username):
    # Issue: XSS via reflected user input in template
    html = f"<h1>Profile: {username}</h1><p>Welcome back!</p>"
    return render_template_string(html)


# --- Config ---


@app.route("/config")
def config():
    # Issue: exposes environment variables
    return jsonify(dict(os.environ))


if __name__ == "__main__":
    init_db()
    # Issue: debug mode in production
    app.run(debug=True, host="0.0.0.0", port=8080)
