#!/usr/bin/env python3
"""learn_english 站点后端：托管静态页 + 登录注册 + 按用户隔离的学习进度/测验成绩。

启动：python3 app.py  →  http://127.0.0.1:5000
"""
import hashlib
import hmac
import os
import re
import sqlite3
from datetime import datetime
from pathlib import Path

from flask import Flask, g, jsonify, request, send_from_directory, session

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "users.db"
SECRET = (BASE_DIR / ".secret_key")

app = Flask(__name__, static_folder=None)

if SECRET.exists():
    app.secret_key = SECRET.read_text().strip()
else:
    app.secret_key = os.urandom(32).hex()
    SECRET.write_text(app.secret_key)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ---------- 数据库 ----------

def db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            pw_salt TEXT NOT NULL,
            pw_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        );
        CREATE TABLE IF NOT EXISTS mastered (
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            word_id INTEGER NOT NULL,
            PRIMARY KEY (user_id, word_id)
        );
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            wrong_ids TEXT NOT NULL DEFAULT '',
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        );
        CREATE TABLE IF NOT EXISTS visits (
            day TEXT PRIMARY KEY,
            count INTEGER NOT NULL DEFAULT 0
        );
        """
    )
    conn.commit()
    conn.close()


def hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 200_000).hex()


def current_user() -> sqlite3.Row | None:
    uid = session.get("uid")
    if uid is None:
        return None
    return db().execute("SELECT id, email FROM users WHERE id = ?", (uid,)).fetchone()


def bad(message: str, code: int = 400):
    return jsonify({"ok": False, "error": message}), code


# ---------- 认证 ----------

@app.post("/api/register")
def register():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    if not EMAIL_RE.match(email):
        return bad("邮箱格式不正确")
    if len(password) < 6:
        return bad("密码至少 6 位")
    conn = db()
    if conn.execute("SELECT 1 FROM users WHERE email = ?", (email,)).fetchone():
        return bad("该邮箱已注册，请直接登录", 409)
    salt = os.urandom(16).hex()
    conn.execute(
        "INSERT INTO users (email, pw_salt, pw_hash) VALUES (?, ?, ?)",
        (email, salt, hash_password(password, salt)),
    )
    conn.commit()
    uid = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()["id"]
    session["uid"] = uid
    return jsonify({"ok": True, "email": email})


@app.post("/api/login")
def login():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    row = db().execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if row is None:
        return bad("邮箱或密码错误", 401)
    if not hmac.compare_digest(hash_password(password, row["pw_salt"]), row["pw_hash"]):
        return bad("邮箱或密码错误", 401)
    session["uid"] = row["id"]
    return jsonify({"ok": True, "email": email})


@app.post("/api/logout")
def logout():
    session.pop("uid", None)
    return jsonify({"ok": True})


@app.get("/api/me")
def me():
    user = current_user()
    if user is None:
        return bad("未登录", 401)
    return jsonify({"ok": True, "email": user["email"]})


# ---------- 今日访问统计 ----------

@app.post("/api/visit")
def visit():
    today = datetime.now().strftime("%Y-%m-%d")
    if session.get("counted_day") != today:
        conn = db()
        conn.execute(
            "INSERT INTO visits (day, count) VALUES (?, 1) "
            "ON CONFLICT(day) DO UPDATE SET count = count + 1",
            (today,),
        )
        conn.commit()
        session["counted_day"] = today
    row = db().execute("SELECT count FROM visits WHERE day = ?", (today,)).fetchone()
    return jsonify({"ok": True, "today": row["count"] if row else 0})


# ---------- 学习进度（按用户隔离） ----------

def require_user():
    user = current_user()
    if user is None:
        return None, bad("未登录", 401)
    return user, None


@app.get("/api/progress")
def get_progress():
    user, err = require_user()
    if err:
        return err
    rows = db().execute(
        "SELECT word_id FROM mastered WHERE user_id = ?", (user["id"],)
    ).fetchall()
    return jsonify({"ok": True, "mastered": [r["word_id"] for r in rows]})


@app.post("/api/progress")
def update_progress():
    user, err = require_user()
    if err:
        return err
    data = request.get_json(silent=True) or {}
    add = [int(x) for x in (data.get("add") or []) if 1 <= int(x) <= 3000]
    remove = [int(x) for x in (data.get("remove") or []) if 1 <= int(x) <= 3000]
    conn = db()
    if add:
        conn.executemany(
            "INSERT OR IGNORE INTO mastered (user_id, word_id) VALUES (?, ?)",
            [(user["id"], x) for x in add],
        )
    if remove:
        conn.executemany(
            "DELETE FROM mastered WHERE user_id = ? AND word_id = ?",
            [(user["id"], x) for x in remove],
        )
    conn.commit()
    return jsonify({"ok": True})


# ---------- 测验成绩（按用户隔离） ----------

@app.get("/api/quiz/history")
def quiz_history():
    user, err = require_user()
    if err:
        return err
    rows = db().execute(
        "SELECT score, total, created_at FROM quiz_results WHERE user_id = ? "
        "ORDER BY id DESC LIMIT 5",
        (user["id"],),
    ).fetchall()
    return jsonify({"ok": True, "history": [dict(r) for r in rows]})


@app.post("/api/quiz/result")
def quiz_result():
    user, err = require_user()
    if err:
        return err
    data = request.get_json(silent=True) or {}
    try:
        score = int(data.get("score"))
        total = int(data.get("total"))
    except (TypeError, ValueError):
        return bad("成绩格式不正确")
    if not (0 <= score <= total <= 100):
        return bad("成绩数值不合法")
    wrong = ",".join(str(int(x)) for x in (data.get("wrong_ids") or [])[:50])
    conn = db()
    conn.execute(
        "INSERT INTO quiz_results (user_id, score, total, wrong_ids) VALUES (?, ?, ?, ?)",
        (user["id"], score, total, wrong),
    )
    conn.commit()
    return jsonify({"ok": True})


# ---------- 静态托管 ----------

ALLOWED = re.compile(r"^[\w\-./]+$")


@app.get("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.get("/<path:filename>")
def static_files(filename: str):
    if not ALLOWED.match(filename):
        return bad("路径不合法", 404)
    target = (BASE_DIR / filename).resolve()
    if not str(target).startswith(str(BASE_DIR)) or not target.is_file():
        return bad("文件不存在", 404)
    return send_from_directory(BASE_DIR, filename)


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=False)
