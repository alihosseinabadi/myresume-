"""Data-access layer: SQLite storage for resumes, cover letters and AI usage."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from typing import Any, Iterator

from config import settings
from models import Resume

SCHEMA = """
CREATE TABLE IF NOT EXISTS resumes (
    id          TEXT PRIMARY KEY,
    title       TEXT NOT NULL,
    template    TEXT NOT NULL,
    locale      TEXT NOT NULL DEFAULT 'en',
    payload     TEXT NOT NULL,
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cover_letters (
    id          TEXT PRIMARY KEY,
    resume_id   TEXT,
    company     TEXT,
    job_title   TEXT,
    body        TEXT NOT NULL,
    provider    TEXT,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ai_events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    feature     TEXT NOT NULL,
    provider    TEXT NOT NULL,
    model       TEXT,
    ok          INTEGER NOT NULL DEFAULT 1,
    latency_ms  INTEGER DEFAULT 0,
    created_at  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_resumes_updated ON resumes (updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_ai_events_feature ON ai_events (feature, created_at DESC);
"""


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    """Yield a row-mapping connection, committing on clean exit."""
    path = settings.database_file
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with connect() as conn:
        conn.executescript(SCHEMA)


def _row_to_resume(row: sqlite3.Row) -> Resume:
    data: dict[str, Any] = json.loads(row["payload"])
    data["id"] = row["id"]
    data["title"] = row["title"]
    data["template"] = row["template"]
    data["locale"] = row["locale"]
    data["created_at"] = row["created_at"]
    data["updated_at"] = row["updated_at"]
    return Resume.model_validate(data)


def save_resume(resume: Resume) -> Resume:
    payload = resume.model_dump(mode="json")
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO resumes (id, title, template, locale, payload, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title = excluded.title,
                template = excluded.template,
                locale = excluded.locale,
                payload = excluded.payload,
                updated_at = excluded.updated_at
            """,
            (
                resume.id,
                resume.title,
                resume.template,
                resume.locale,
                json.dumps(payload, ensure_ascii=False),
                resume.created_at.isoformat(),
                resume.updated_at.isoformat(),
            ),
        )
    return resume


def list_resumes(limit: int = 50) -> list[Resume]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM resumes ORDER BY updated_at DESC LIMIT ?", (limit,)
        ).fetchall()
    return [_row_to_resume(r) for r in rows]


def get_resume(resume_id: str) -> Resume | None:
    with connect() as conn:
        row = conn.execute("SELECT * FROM resumes WHERE id = ?", (resume_id,)).fetchone()
    return _row_to_resume(row) if row else None


def delete_resume(resume_id: str) -> bool:
    with connect() as conn:
        cur = conn.execute("DELETE FROM resumes WHERE id = ?", (resume_id,))
    return cur.rowcount > 0


def count_resumes() -> int:
    with connect() as conn:
        return int(conn.execute("SELECT COUNT(*) FROM resumes").fetchone()[0])


def save_cover_letter(
    letter_id: str,
    body: str,
    resume_id: str = "",
    company: str = "",
    job_title: str = "",
    provider: str = "local",
    created_at: str = "",
) -> None:
    with connect() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO cover_letters
                (id, resume_id, company, job_title, body, provider, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (letter_id, resume_id, company, job_title, body, provider, created_at),
        )


def list_cover_letters(limit: int = 50) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM cover_letters ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


def log_ai_event(
    feature: str,
    provider: str,
    model: str = "",
    ok: bool = True,
    latency_ms: int = 0,
) -> None:
    from datetime import datetime, timezone

    with connect() as conn:
        conn.execute(
            """
            INSERT INTO ai_events (feature, provider, model, ok, latency_ms, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                feature,
                provider,
                model,
                1 if ok else 0,
                latency_ms,
                datetime.now(timezone.utc).isoformat(),
            ),
        )


def ai_usage(days: int = 7) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT feature, provider, COUNT(*) AS calls, AVG(latency_ms) AS avg_latency_ms
            FROM ai_events
            WHERE created_at >= datetime('now', ?)
            GROUP BY feature, provider
            ORDER BY calls DESC
            """,
            (f"-{days} days",),
        ).fetchall()
    return [dict(r) for r in rows]
