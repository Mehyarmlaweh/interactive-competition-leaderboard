import sqlite3
import pandas as pd
import hashlib
import secrets
import string

DB_NAME = "leaderboard.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS students (
        token TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        display_name TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        token TEXT NOT NULL,
        score REAL NOT NULL,
        attempt INTEGER NOT NULL DEFAULT 1,
        submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (token) REFERENCES students(token)
    )
    """)

    conn.commit()
    conn.close()


def generate_token(length=12):
    """Generate a random alphanumeric token."""
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def register_student(name: str, token: str = None) -> str:
    """
    Register a student and return their token.
    If token is provided, use it (instructor-assigned).
    Otherwise generate a random one.
    """
    conn = sqlite3.connect(DB_NAME)

    if token is None:
        token = generate_token()

    # Ensure uniqueness
    while True:
        existing = conn.execute(
            "SELECT token FROM students WHERE token = ?", (token,)
        ).fetchone()
        if not existing:
            break
        token = generate_token()

    display_name = name.strip()

    conn.execute(
        "INSERT INTO students (token, name, display_name) VALUES (?, ?, ?)",
        (token, name.strip().lower(), display_name)
    )
    conn.commit()
    conn.close()
    return token


def validate_token(token: str):
    """Returns student info dict if token is valid, else None."""
    conn = sqlite3.connect(DB_NAME)
    row = conn.execute(
        "SELECT token, display_name FROM students WHERE token = ?",
        (token.strip().upper(),)
    ).fetchone()
    conn.close()
    if row:
        return {"token": row[0], "display_name": row[1]}
    return None


def submit_score(token: str, score: float):
    """Submit a score. Each student can submit multiple times; best score is shown."""
    conn = sqlite3.connect(DB_NAME)

    attempt = conn.execute(
        "SELECT COUNT(*) FROM submissions WHERE token = ?", (token,)
    ).fetchone()[0] + 1

    conn.execute(
        "INSERT INTO submissions (token, score, attempt) VALUES (?, ?, ?)",
        (token, score, attempt)
    )
    conn.commit()
    conn.close()


def get_leaderboard():
    """Returns leaderboard with best score per student, ranked."""
    conn = sqlite3.connect(DB_NAME)

    df = pd.read_sql(
        """
        SELECT
            s.display_name as name,
            MAX(sub.score) as score,
            COUNT(sub.id) as attempts,
            MAX(sub.submitted_at) as last_submission
        FROM students s
        JOIN submissions sub ON s.token = sub.token
        GROUP BY s.token, s.display_name
        ORDER BY score DESC
        """,
        conn
    )

    conn.close()
    return df


def get_submission_history(token: str):
    """Get all submissions for a student."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql(
        """
        SELECT attempt, score, submitted_at
        FROM submissions
        WHERE token = ?
        ORDER BY attempt ASC
        """,
        conn,
        params=(token,)
    )
    conn.close()
    return df


def get_total_students():
    conn = sqlite3.connect(DB_NAME)
    count = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    conn.close()
    return count


def get_total_submissions():
    conn = sqlite3.connect(DB_NAME)
    count = conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0]
    conn.close()
    return count


# ── Admin helpers ──────────────────────────────────────────────────────────────

def bulk_register_students(names: list[str]) -> list[dict]:
    """Register multiple students at once. Returns list of {name, token}."""
    results = []
    for name in names:
        if name.strip():
            token = register_student(name.strip())
            results.append({"name": name.strip(), "token": token})
    return results


def get_all_students():
    """Admin: get all registered students and their tokens."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT display_name as name, token, created_at FROM students ORDER BY created_at", conn)
    conn.close()
    return df


def reset_leaderboard():
    """Admin: wipe all submissions (keeps students)."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("DELETE FROM submissions")
    conn.commit()
    conn.close()


def delete_student(token: str):
    """Admin: remove a student and all their submissions."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("DELETE FROM submissions WHERE token = ?", (token,))
    conn.execute("DELETE FROM students WHERE token = ?", (token,))
    conn.commit()
    conn.close()