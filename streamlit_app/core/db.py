"""Stato condiviso su SQLite: pronostici e risultati.

Lo scorer è salvato come JSON: lista di {"team": str, "name": str}.
Le doppiette sono rappresentate da voci ripetute.
"""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path

_DB_PATH = Path(os.environ.get("WC26_DB", Path(__file__).resolve().parents[1] / "wc26.db"))


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(_DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    return conn


def init_db() -> None:
    with _conn() as c:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS predictions (
                user_id TEXT NOT NULL,
                match_id INTEGER NOT NULL,
                home INTEGER NOT NULL,
                away INTEGER NOT NULL,
                scorers TEXT NOT NULL DEFAULT '[]',
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                PRIMARY KEY (user_id, match_id)
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS results (
                match_id INTEGER PRIMARY KEY,
                home INTEGER NOT NULL,
                away INTEGER NOT NULL,
                scorers TEXT NOT NULL DEFAULT '[]',
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        c.execute(
            "CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)"
        )


def set_meta(key: str, value: str) -> None:
    with _conn() as c:
        c.execute(
            "INSERT INTO meta (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )


def get_meta(key: str) -> str | None:
    with _conn() as c:
        row = c.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
    return row["value"] if row else None


def _row_to_pred(row: sqlite3.Row) -> dict:
    return {
        "user_id": row["user_id"],
        "match_id": row["match_id"],
        "home": row["home"],
        "away": row["away"],
        "scorers": json.loads(row["scorers"]),
    }


def _row_to_result(row: sqlite3.Row) -> dict:
    return {
        "match_id": row["match_id"],
        "home": row["home"],
        "away": row["away"],
        "scorers": json.loads(row["scorers"]),
    }


def get_prediction(user_id: str, match_id: int) -> dict | None:
    with _conn() as c:
        row = c.execute(
            "SELECT * FROM predictions WHERE user_id=? AND match_id=?",
            (user_id, match_id),
        ).fetchone()
    return _row_to_pred(row) if row else None


def all_predictions() -> list[dict]:
    with _conn() as c:
        rows = c.execute("SELECT * FROM predictions").fetchall()
    return [_row_to_pred(r) for r in rows]


def save_prediction(user_id: str, match_id: int, home: int, away: int, scorers: list[dict]) -> None:
    with _conn() as c:
        c.execute(
            """
            INSERT INTO predictions (user_id, match_id, home, away, scorers, updated_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
            ON CONFLICT(user_id, match_id) DO UPDATE SET
                home=excluded.home, away=excluded.away,
                scorers=excluded.scorers, updated_at=datetime('now')
            """,
            (user_id, match_id, int(home), int(away), json.dumps(scorers, ensure_ascii=False)),
        )


def delete_prediction(user_id: str, match_id: int) -> None:
    with _conn() as c:
        c.execute("DELETE FROM predictions WHERE user_id=? AND match_id=?", (user_id, match_id))


def get_result(match_id: int) -> dict | None:
    with _conn() as c:
        row = c.execute("SELECT * FROM results WHERE match_id=?", (match_id,)).fetchone()
    return _row_to_result(row) if row else None


def all_results() -> dict[int, dict]:
    with _conn() as c:
        rows = c.execute("SELECT * FROM results").fetchall()
    return {r["match_id"]: _row_to_result(r) for r in rows}


def save_result(match_id: int, home: int, away: int, scorers: list[dict]) -> None:
    with _conn() as c:
        c.execute(
            """
            INSERT INTO results (match_id, home, away, scorers, updated_at)
            VALUES (?, ?, ?, ?, datetime('now'))
            ON CONFLICT(match_id) DO UPDATE SET
                home=excluded.home, away=excluded.away,
                scorers=excluded.scorers, updated_at=datetime('now')
            """,
            (match_id, int(home), int(away), json.dumps(scorers, ensure_ascii=False)),
        )


def delete_result(match_id: int) -> None:
    with _conn() as c:
        c.execute("DELETE FROM results WHERE match_id=?", (match_id,))
