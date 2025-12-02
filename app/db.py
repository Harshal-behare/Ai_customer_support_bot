import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Generator, List, Optional

from .config import DB_PATH


@contextmanager
def get_connection() -> Generator[sqlite3.Connection, None, None]:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT NOT NULL,
                bot_response TEXT NOT NULL,
                intent TEXT,
                confidence REAL,
                created_at TEXT NOT NULL,
                session_id TEXT NOT NULL DEFAULT 'default'
            );
            """
        )
        ensure_chat_log_schema(conn)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT NOT NULL,
                status TEXT NOT NULL,
                priority TEXT NOT NULL,
                created_at TEXT NOT NULL,
                bot_confidence REAL
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_log_id INTEGER NOT NULL,
                rating TEXT NOT NULL,
                comment TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(chat_log_id) REFERENCES chat_logs(id)
            );
            """
        )


def ensure_chat_log_schema(conn: sqlite3.Connection) -> None:
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(chat_logs)")}
    if "session_id" not in columns:
        conn.execute("ALTER TABLE chat_logs ADD COLUMN session_id TEXT NOT NULL DEFAULT 'default'")


def insert_chat_log(
    user_message: str,
    bot_response: str,
    intent: Optional[str],
    confidence: float,
    session_id: str,
) -> int:
    created_at = datetime.utcnow().isoformat()
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO chat_logs (user_message, bot_response, intent, confidence, created_at, session_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_message, bot_response, intent, confidence, created_at, session_id),
        )
        return cursor.lastrowid


def insert_ticket(user_message: str, priority: str, bot_confidence: Optional[float]) -> int:
    created_at = datetime.utcnow().isoformat()
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO tickets (user_message, status, priority, created_at, bot_confidence)
            VALUES (?, 'open', ?, ?, ?)
            """,
            (user_message, priority, created_at, bot_confidence),
        )
        return cursor.lastrowid


def list_tickets() -> List[sqlite3.Row]:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT id, user_message, status, priority, created_at, bot_confidence
            FROM tickets
            ORDER BY created_at DESC
            """
        )
        return cursor.fetchall()


def insert_feedback(chat_log_id: int, rating: str, comment: Optional[str]) -> int:
    created_at = datetime.utcnow().isoformat()
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO feedback (chat_log_id, rating, comment, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (chat_log_id, rating, comment, created_at),
        )
        return cursor.lastrowid


def recent_chat_history(session_id: str, limit: int = 5) -> List[sqlite3.Row]:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT id, user_message, bot_response, created_at
            FROM chat_logs
            WHERE session_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (session_id, limit),
        )
        return cursor.fetchall()
