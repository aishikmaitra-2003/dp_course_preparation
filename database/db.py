"""
DP-700 Exam Prep — SQLite Database Manager
Handles all persistence: journal, chat history, quizzes, progress, weaknesses.
"""

import sqlite3
import json
import os
from datetime import datetime
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dp700_prep.db")


@contextmanager
def get_connection():
    """Thread-safe SQLite connection context manager."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Create all tables if they don't exist."""
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS journal_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_id INTEGER NOT NULL,
                title TEXT NOT NULL DEFAULT 'Untitled Note',
                content TEXT NOT NULL DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_id INTEGER NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
                content TEXT NOT NULL,
                model_used TEXT DEFAULT '',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_id INTEGER,
                quiz_type TEXT NOT NULL CHECK(quiz_type IN ('module', 'final')),
                score INTEGER NOT NULL,
                total INTEGER NOT NULL,
                questions_data TEXT DEFAULT '[]',
                weakness_areas TEXT DEFAULT '[]',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS study_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_id INTEGER NOT NULL UNIQUE,
                status TEXT NOT NULL DEFAULT 'not_started'
                    CHECK(status IN ('not_started', 'in_progress', 'completed')),
                time_spent_mins INTEGER DEFAULT 0,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS user_weaknesses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_id INTEGER NOT NULL,
                topic TEXT NOT NULL,
                weakness_score REAL DEFAULT 0.5,
                identified_from TEXT DEFAULT 'quiz',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)


# ---------------------------------------------------------------------------
# Journal CRUD
# ---------------------------------------------------------------------------

def save_journal_entry(module_id: int, title: str, content: str, entry_id: int = None):
    """Create or update a journal entry."""
    with get_connection() as conn:
        now = datetime.now().isoformat()
        if entry_id:
            conn.execute(
                "UPDATE journal_entries SET title=?, content=?, updated_at=? WHERE id=?",
                (title, content, now, entry_id),
            )
            return entry_id
        else:
            cursor = conn.execute(
                "INSERT INTO journal_entries (module_id, title, content, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                (module_id, title, content, now, now),
            )
            return cursor.lastrowid


def get_journal_entries(module_id: int = None):
    """Get journal entries, optionally filtered by module."""
    with get_connection() as conn:
        if module_id is not None:
            rows = conn.execute(
                "SELECT * FROM journal_entries WHERE module_id=? ORDER BY updated_at DESC",
                (module_id,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM journal_entries ORDER BY updated_at DESC"
            ).fetchall()
        return [dict(r) for r in rows]


def delete_journal_entry(entry_id: int):
    """Delete a journal entry by ID."""
    with get_connection() as conn:
        conn.execute("DELETE FROM journal_entries WHERE id=?", (entry_id,))


# ---------------------------------------------------------------------------
# Chat History
# ---------------------------------------------------------------------------

def save_chat_message(module_id: int, role: str, content: str, model_used: str = ""):
    """Save a single chat message."""
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO chat_history (module_id, role, content, model_used) VALUES (?, ?, ?, ?)",
            (module_id, role, content, model_used),
        )


def get_chat_history(module_id: int, limit: int = 50):
    """Get chat history for a module."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM chat_history WHERE module_id=? ORDER BY timestamp ASC LIMIT ?",
            (module_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]


def get_all_chat_history_for_quiz(module_id: int):
    """Get all user messages for a module (used by quiz generator to find weak areas)."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT content FROM chat_history WHERE module_id=? AND role='user' ORDER BY timestamp ASC",
            (module_id,),
        ).fetchall()
        return [r["content"] for r in rows]


def clear_chat_history(module_id: int):
    """Clear all chat history for a module."""
    with get_connection() as conn:
        conn.execute("DELETE FROM chat_history WHERE module_id=?", (module_id,))


# ---------------------------------------------------------------------------
# Quiz Results
# ---------------------------------------------------------------------------

def save_quiz_result(module_id: int, quiz_type: str, score: int, total: int,
                     questions_data: list = None, weakness_areas: list = None):
    """Save a quiz result."""
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO quiz_results (module_id, quiz_type, score, total, questions_data, weakness_areas) VALUES (?, ?, ?, ?, ?, ?)",
            (
                module_id,
                quiz_type,
                score,
                total,
                json.dumps(questions_data or []),
                json.dumps(weakness_areas or []),
            ),
        )


def get_quiz_results(module_id: int = None, quiz_type: str = None):
    """Get quiz results with optional filters."""
    with get_connection() as conn:
        query = "SELECT * FROM quiz_results WHERE 1=1"
        params = []
        if module_id is not None:
            query += " AND module_id=?"
            params.append(module_id)
        if quiz_type:
            query += " AND quiz_type=?"
            params.append(quiz_type)
        query += " ORDER BY timestamp DESC"
        rows = conn.execute(query, params).fetchall()
        results = []
        for r in rows:
            d = dict(r)
            d["questions_data"] = json.loads(d.get("questions_data", "[]"))
            d["weakness_areas"] = json.loads(d.get("weakness_areas", "[]"))
            results.append(d)
        return results


# ---------------------------------------------------------------------------
# Study Progress
# ---------------------------------------------------------------------------

def update_progress(module_id: int, status: str = None, add_time_mins: int = 0):
    """Update study progress for a module."""
    with get_connection() as conn:
        existing = conn.execute(
            "SELECT * FROM study_progress WHERE module_id=?", (module_id,)
        ).fetchone()
        now = datetime.now().isoformat()
        if existing:
            new_status = status or existing["status"]
            new_time = existing["time_spent_mins"] + add_time_mins
            conn.execute(
                "UPDATE study_progress SET status=?, time_spent_mins=?, last_accessed=? WHERE module_id=?",
                (new_status, new_time, now, module_id),
            )
        else:
            conn.execute(
                "INSERT INTO study_progress (module_id, status, time_spent_mins, last_accessed) VALUES (?, ?, ?, ?)",
                (module_id, status or "not_started", add_time_mins, now),
            )


def get_all_progress():
    """Get progress for all modules."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM study_progress ORDER BY module_id"
        ).fetchall()
        return [dict(r) for r in rows]


def get_module_progress(module_id: int):
    """Get progress for a specific module."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM study_progress WHERE module_id=?", (module_id,)
        ).fetchone()
        return dict(row) if row else None


# ---------------------------------------------------------------------------
# Weaknesses
# ---------------------------------------------------------------------------

def save_weakness(module_id: int, topic: str, score: float, source: str = "quiz"):
    """Save or update a weakness entry."""
    with get_connection() as conn:
        existing = conn.execute(
            "SELECT id FROM user_weaknesses WHERE module_id=? AND topic=?",
            (module_id, topic),
        ).fetchone()
        now = datetime.now().isoformat()
        if existing:
            conn.execute(
                "UPDATE user_weaknesses SET weakness_score=?, identified_from=?, updated_at=? WHERE id=?",
                (score, source, now, existing["id"]),
            )
        else:
            conn.execute(
                "INSERT INTO user_weaknesses (module_id, topic, weakness_score, identified_from, updated_at) VALUES (?, ?, ?, ?, ?)",
                (module_id, topic, score, source, now),
            )


def get_weaknesses(module_id: int = None):
    """Get weakness areas, optionally filtered by module."""
    with get_connection() as conn:
        if module_id is not None:
            rows = conn.execute(
                "SELECT * FROM user_weaknesses WHERE module_id=? ORDER BY weakness_score DESC",
                (module_id,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM user_weaknesses ORDER BY weakness_score DESC"
            ).fetchall()
        return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Analytics helpers
# ---------------------------------------------------------------------------

def get_analytics_summary():
    """Aggregate analytics for the dashboard."""
    with get_connection() as conn:
        # Modules completed
        completed = conn.execute(
            "SELECT COUNT(*) as cnt FROM study_progress WHERE status='completed'"
        ).fetchone()["cnt"]

        # Total time
        total_time = conn.execute(
            "SELECT COALESCE(SUM(time_spent_mins), 0) as total FROM study_progress"
        ).fetchone()["total"]

        # Average quiz score
        avg_score = conn.execute(
            "SELECT COALESCE(AVG(CAST(score AS REAL) / total * 100), 0) as avg FROM quiz_results WHERE total > 0"
        ).fetchone()["avg"]

        # Total quizzes taken
        total_quizzes = conn.execute(
            "SELECT COUNT(*) as cnt FROM quiz_results"
        ).fetchone()["cnt"]

        # Total journal entries
        total_notes = conn.execute(
            "SELECT COUNT(*) as cnt FROM journal_entries"
        ).fetchone()["cnt"]

        # Total chat messages
        total_chats = conn.execute(
            "SELECT COUNT(*) as cnt FROM chat_history WHERE role='user'"
        ).fetchone()["cnt"]

        return {
            "modules_completed": completed,
            "total_time_mins": total_time,
            "avg_quiz_score": round(avg_score, 1),
            "total_quizzes": total_quizzes,
            "total_notes": total_notes,
            "total_chats": total_chats,
        }
