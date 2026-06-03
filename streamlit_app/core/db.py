"""Stato condiviso: pronostici e risultati.

Backend duale:
  - locale  -> sqlite3 (sviluppo, file wc26.db)
  - remoto  -> Turso/libSQL quando TURSO_DATABASE_URL è impostata (deploy persistente
               su filesystem effimero, es. Streamlit Community Cloud).

Le query usano sempre colonne esplicite e mappatura per indice, così funzionano
identiche con sqlite3.Row e con le tuple restituite da libsql.

Lo scorer è salvato come JSON: lista di {"team": str, "name": str}.
Le doppiette sono rappresentate da voci ripetute.
"""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path

_DB_PATH = Path(os.environ.get("WC26_DB", Path(__file__).resolve().parents[1] / "wc26.db"))


def _turso_creds() -> tuple[str | None, str | None]:
    """URL + token Turso da env oppure da st.secrets (solo nel processo dell'app)."""
    url = os.environ.get("TURSO_DATABASE_URL")
    token = os.environ.get("TURSO_AUTH_TOKEN")
    if not url:
        try:
            import streamlit as st

            url = st.secrets.get("TURSO_DATABASE_URL")
            token = st.secrets.get("TURSO_AUTH_TOKEN")
        except Exception:
            pass
    return url, token


def is_remote() -> bool:
    return bool(_turso_creds()[0])


class _RemoteCursor:
    """Adatta il ResultSet di libsql-client all'interfaccia fetchone/fetchall.

    Le Row di libsql-client supportano l'accesso per indice (row[0]), come
    le tuple di sqlite3: la mappatura per indice resta quindi identica.
    """

    def __init__(self, rows) -> None:  # noqa: ANN001
        self._rows = rows

    def fetchone(self):  # noqa: ANN201
        return self._rows[0] if self._rows else None

    def fetchall(self):  # noqa: ANN201
        return self._rows


class _Conn:
    """Wrapper minimale che uniforma sqlite3 (locale) e Turso/libSQL (remoto).

    - Locale: sqlite3, commit esplicito al termine del blocco `with`.
    - Remoto: libsql-client (HTTP), ogni statement è autocommit; `commit()`
      è un no-op.
    """

    def __init__(self) -> None:
        url, token = _turso_creds()
        if url:
            from libsql_client import create_client_sync

            if url.startswith("libsql://"):
                url = "https://" + url[len("libsql://"):]
            self._client = create_client_sync(url=url, auth_token=token or None)
            self._remote = True
        else:
            c = sqlite3.connect(_DB_PATH, timeout=10)
            c.execute("PRAGMA journal_mode=WAL;")
            c.execute("PRAGMA busy_timeout=5000;")
            self._c = c
            self._remote = False

    def execute(self, sql: str, params: tuple = ()):  # noqa: ANN001
        if self._remote:
            rs = self._client.execute(sql, list(params))
            return _RemoteCursor(rs.rows)
        cur = self._c.cursor()
        cur.execute(sql, tuple(params))
        return cur

    def commit(self) -> None:
        if not self._remote:
            self._c.commit()

    def close(self) -> None:
        try:
            (self._client if self._remote else self._c).close()
        except Exception:
            pass

    def __enter__(self) -> "_Conn":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:  # noqa: ANN001
        if exc_type is None:
            self.commit()
        self.close()
        return False


def init_db() -> None:
    with _Conn() as c:
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
        c.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")


def set_meta(key: str, value: str) -> None:
    with _Conn() as c:
        c.execute(
            "INSERT INTO meta (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )


def get_meta(key: str) -> str | None:
    with _Conn() as c:
        row = c.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
    return row[0] if row else None


def _to_pred(row) -> dict:  # noqa: ANN001
    return {
        "user_id": row[0],
        "match_id": row[1],
        "home": row[2],
        "away": row[3],
        "scorers": json.loads(row[4]),
    }


def _to_result(row) -> dict:  # noqa: ANN001
    return {
        "match_id": row[0],
        "home": row[1],
        "away": row[2],
        "scorers": json.loads(row[3]),
    }


def get_prediction(user_id: str, match_id: int) -> dict | None:
    with _Conn() as c:
        row = c.execute(
            "SELECT user_id, match_id, home, away, scorers "
            "FROM predictions WHERE user_id=? AND match_id=?",
            (user_id, match_id),
        ).fetchone()
    return _to_pred(row) if row else None


def all_predictions() -> list[dict]:
    with _Conn() as c:
        rows = c.execute(
            "SELECT user_id, match_id, home, away, scorers FROM predictions"
        ).fetchall()
    return [_to_pred(r) for r in rows]


def save_prediction(user_id: str, match_id: int, home: int, away: int, scorers: list[dict]) -> None:
    with _Conn() as c:
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
    with _Conn() as c:
        c.execute("DELETE FROM predictions WHERE user_id=? AND match_id=?", (user_id, match_id))


def get_result(match_id: int) -> dict | None:
    with _Conn() as c:
        row = c.execute(
            "SELECT match_id, home, away, scorers FROM results WHERE match_id=?",
            (match_id,),
        ).fetchone()
    return _to_result(row) if row else None


def all_results() -> dict[int, dict]:
    with _Conn() as c:
        rows = c.execute("SELECT match_id, home, away, scorers FROM results").fetchall()
    return {r[0]: _to_result(r) for r in rows}


def save_result(match_id: int, home: int, away: int, scorers: list[dict]) -> None:
    with _Conn() as c:
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
    with _Conn() as c:
        c.execute("DELETE FROM results WHERE match_id=?", (match_id,))
