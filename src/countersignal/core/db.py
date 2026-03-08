"""SQLite database operations for CounterSignal campaigns and hits.

This module provides all database functionality for persisting and retrieving
campaign and hit data. Uses SQLite with automatic schema migrations for
backward compatibility.

Typical usage:
    >>> from countersignal.core.db import init_db, save_campaign, get_campaign
    >>> init_db()  # Initialize schema (safe to call multiple times)
    >>> save_campaign(campaign)
    >>> retrieved = get_campaign(campaign.uuid)

Database location:
    Default: ~/.countersignal/ipi.db
    Override: Pass db_path parameter to any function

Schema:
    - campaigns: Tracks generated payload documents
    - hits: Records callback requests received from AI agents
"""

import json
import sqlite3
from collections.abc import Generator
from contextlib import contextmanager, suppress
from datetime import datetime
from pathlib import Path

from .models import Campaign, Hit, HitConfidence

DEFAULT_DB_PATH = Path.home() / ".countersignal" / "ipi.db"
"""Default database file location (~/.countersignal/ipi.db)."""


@contextmanager
def get_connection(db_path: Path = DEFAULT_DB_PATH) -> Generator[sqlite3.Connection, None, None]:
    """Get a database connection with automatic transaction management.

    Context manager that provides a SQLite connection with:
    - Automatic directory creation for the database file
    - Row factory set to sqlite3.Row for dict-like access
    - Automatic commit on successful exit
    - Automatic rollback on exception
    - Guaranteed connection closure

    Args:
        db_path: Path to the SQLite database file.
            Defaults to DEFAULT_DB_PATH (~/.countersignal/ipi.db).

    Yields:
        sqlite3.Connection: Active database connection.

    Raises:
        sqlite3.Error: On database connection or operation failures.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(db_path: Path = DEFAULT_DB_PATH) -> None:
    """Initialize the database schema with migrations.

    Creates the campaigns and hits tables if they don't exist, and applies
    any necessary migrations for backward compatibility with older databases.

    Safe to call multiple times - uses CREATE TABLE IF NOT EXISTS and
    catches column-already-exists errors for migrations.

    Args:
        db_path: Path to the SQLite database file.
            Defaults to DEFAULT_DB_PATH.

    Raises:
        sqlite3.Error: On database initialization failures.
    """
    with get_connection(db_path) as conn:
        # Optimization: check version first to avoid redundant DDL operations
        if conn.execute("PRAGMA user_version").fetchone()[0] < 1:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS campaigns (
                    uuid TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    format TEXT NOT NULL DEFAULT 'pdf',
                    technique TEXT NOT NULL,
                    callback_url TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_style TEXT DEFAULT 'obvious',
                    payload_type TEXT DEFAULT 'callback'
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS hits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    uuid TEXT NOT NULL,
                    source_ip TEXT NOT NULL,
                    user_agent TEXT NOT NULL,
                    headers TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (uuid) REFERENCES campaigns(uuid)
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_hits_uuid ON hits(uuid)")

            # Migration: add payload_style column if it doesn't exist (for existing DBs)
            with suppress(sqlite3.OperationalError):
                conn.execute(
                    "ALTER TABLE campaigns ADD COLUMN payload_style TEXT DEFAULT 'obvious'"
                )

            # Migration: add format and payload_type columns for existing DBs
            with suppress(sqlite3.OperationalError):
                conn.execute("ALTER TABLE campaigns ADD COLUMN format TEXT DEFAULT 'pdf'")
            with suppress(sqlite3.OperationalError):
                conn.execute(
                    "ALTER TABLE campaigns ADD COLUMN payload_type TEXT DEFAULT 'callback'"
                )

            conn.execute("PRAGMA user_version = 1")

        # Migration v2: add body column to hits for exfil data capture (Phase 4)
        if conn.execute("PRAGMA user_version").fetchone()[0] < 2:
            with suppress(sqlite3.OperationalError):
                conn.execute("ALTER TABLE hits ADD COLUMN body TEXT DEFAULT NULL")
            conn.execute("PRAGMA user_version = 2")

        # Migration v3: authenticated callbacks (Phase 5)
        # Add token to campaigns, token_valid + confidence to hits
        if conn.execute("PRAGMA user_version").fetchone()[0] < 3:
            with suppress(sqlite3.OperationalError):
                conn.execute("ALTER TABLE campaigns ADD COLUMN token TEXT DEFAULT ''")
            with suppress(sqlite3.OperationalError):
                conn.execute("ALTER TABLE hits ADD COLUMN token_valid INTEGER NOT NULL DEFAULT 0")
            with suppress(sqlite3.OperationalError):
                conn.execute("ALTER TABLE hits ADD COLUMN confidence TEXT NOT NULL DEFAULT 'low'")
            conn.execute("PRAGMA user_version = 3")

        # Migration v4: add output_path to campaigns for file cleanup on reset
        if conn.execute("PRAGMA user_version").fetchone()[0] < 4:
            with suppress(sqlite3.OperationalError):
                conn.execute("ALTER TABLE campaigns ADD COLUMN output_path TEXT DEFAULT NULL")
            conn.execute("PRAGMA user_version = 4")


def save_campaign(campaign: Campaign, db_path: Path = DEFAULT_DB_PATH) -> None:
    """Save a campaign to the database.

    Inserts a new campaign record. The campaign's UUID must be unique.

    Args:
        campaign: Campaign model instance to persist.
        db_path: Path to the SQLite database file.
            Defaults to DEFAULT_DB_PATH.

    Raises:
        sqlite3.IntegrityError: If a campaign with the same UUID exists.
        sqlite3.Error: On other database failures.
    """
    with get_connection(db_path) as conn:
        conn.execute(
            """
            INSERT INTO campaigns (
                uuid, token, filename, output_path, format, technique, callback_url,
                created_at, payload_style, payload_type
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                campaign.uuid,
                campaign.token,
                campaign.filename,
                campaign.output_path,
                campaign.format,
                campaign.technique,
                campaign.callback_url,
                campaign.created_at.isoformat(),
                campaign.payload_style,
                campaign.payload_type,
            ),
        )


def save_hit(hit: Hit, db_path: Path = DEFAULT_DB_PATH) -> None:
    """Save a callback hit to the database.

    Inserts a new hit record. The hit's UUID should reference an existing
    campaign, though this is not enforced at the database level.

    Args:
        hit: Hit model instance to persist.
        db_path: Path to the SQLite database file.
            Defaults to DEFAULT_DB_PATH.

    Raises:
        sqlite3.Error: On database failures.
    """
    with get_connection(db_path) as conn:
        conn.execute(
            """
            INSERT INTO hits (uuid, source_ip, user_agent, headers, body,
                            token_valid, confidence, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                hit.uuid,
                hit.source_ip,
                hit.user_agent,
                json.dumps(hit.headers),
                hit.body,
                1 if hit.token_valid else 0,
                hit.confidence.value,
                hit.timestamp.isoformat(),
            ),
        )


def _row_to_campaign(row: sqlite3.Row) -> Campaign:
    """Convert a SQLite row to a Campaign instance."""
    return Campaign(
        uuid=row["uuid"],
        token=row["token"] or "",
        filename=row["filename"],
        output_path=row["output_path"],
        format=row["format"] or "pdf",
        technique=row["technique"],
        payload_style=row["payload_style"] or "obvious",
        payload_type=row["payload_type"] or "callback",
        callback_url=row["callback_url"],
        created_at=datetime.fromisoformat(row["created_at"]),
    )


def get_campaign_by_token(
    uuid: str, token: str, db_path: Path = DEFAULT_DB_PATH
) -> Campaign | None:
    """Retrieve a campaign by UUID and validate its authentication token.

    Used by the callback server to validate authenticated callback URLs.
    Returns the campaign only if both UUID and token match.

    Args:
        uuid: The unique identifier of the campaign.
        token: The authentication token to validate.
        db_path: Path to the SQLite database file.
            Defaults to DEFAULT_DB_PATH.

    Returns:
        Campaign instance if UUID exists and token matches, None otherwise.

    Raises:
        sqlite3.Error: On database failures.
    """
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM campaigns WHERE uuid = ? AND token = ?", (uuid, token)
        ).fetchone()
        if row:
            return _row_to_campaign(row)
        return None


def get_campaign(uuid: str, db_path: Path = DEFAULT_DB_PATH) -> Campaign | None:
    """Retrieve a campaign by its UUID.

    Args:
        uuid: The unique identifier of the campaign to retrieve.
        db_path: Path to the SQLite database file.
            Defaults to DEFAULT_DB_PATH.

    Returns:
        Campaign instance if found, None otherwise.

    Raises:
        sqlite3.Error: On database failures.
    """
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT * FROM campaigns WHERE uuid = ?", (uuid,)).fetchone()
        if row:
            return _row_to_campaign(row)
        return None


def get_hits(uuid: str | None = None, db_path: Path = DEFAULT_DB_PATH) -> list[Hit]:
    """Retrieve callback hits, optionally filtered by campaign UUID.

    Args:
        uuid: If provided, only return hits for this campaign.
            If None, return all hits.
        db_path: Path to the SQLite database file.
            Defaults to DEFAULT_DB_PATH.

    Returns:
        List of Hit instances, ordered by timestamp descending (newest first).
        Empty list if no hits found.

    Raises:
        sqlite3.Error: On database failures.
    """
    with get_connection(db_path) as conn:
        if uuid:
            rows = conn.execute(
                "SELECT * FROM hits WHERE uuid = ? ORDER BY timestamp DESC", (uuid,)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM hits ORDER BY timestamp DESC").fetchall()
        return [
            Hit(
                id=row["id"],
                uuid=row["uuid"],
                source_ip=row["source_ip"],
                user_agent=row["user_agent"],
                headers=json.loads(row["headers"]),
                body=row["body"],
                token_valid=bool(row["token_valid"]),
                confidence=HitConfidence(row["confidence"]),
                timestamp=datetime.fromisoformat(row["timestamp"]),
            )
            for row in rows
        ]


def reset_db(db_path: Path = DEFAULT_DB_PATH) -> tuple[int, int, int]:
    """Delete all campaigns, hits, and generated files.

    Reads output paths from campaigns, deletes the corresponding files
    from disk, then clears both database tables. The schema is preserved.

    Args:
        db_path: Path to the SQLite database file.
            Defaults to DEFAULT_DB_PATH.

    Returns:
        Tuple of (campaigns_deleted, hits_deleted, files_deleted) counts.

    Raises:
        sqlite3.Error: On database failures.
    """
    files_deleted = 0
    with get_connection(db_path) as conn:
        # Collect and delete generated files before clearing DB
        rows = conn.execute("SELECT output_path FROM campaigns WHERE output_path IS NOT NULL")
        for row in rows:
            file_path = Path(row["output_path"])
            if file_path.is_file():
                file_path.unlink()
                files_deleted += 1

        hits_deleted = conn.execute("DELETE FROM hits").rowcount
        campaigns_deleted = conn.execute("DELETE FROM campaigns").rowcount
        return campaigns_deleted, hits_deleted, files_deleted


def get_all_campaigns(db_path: Path = DEFAULT_DB_PATH) -> list[Campaign]:
    """Retrieve all campaigns from the database.

    Args:
        db_path: Path to the SQLite database file.
            Defaults to DEFAULT_DB_PATH.

    Returns:
        List of all Campaign instances, ordered by created_at descending
        (newest first). Empty list if no campaigns exist.

    Raises:
        sqlite3.Error: On database failures.
    """
    with get_connection(db_path) as conn:
        rows = conn.execute("SELECT * FROM campaigns ORDER BY created_at DESC").fetchall()
        return [_row_to_campaign(row) for row in rows]
