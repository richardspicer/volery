"""Regression tests for sqlite3.Row read-path correctness.

Verifies that values written to the database are read back accurately,
catching the bug where ``"column_name" in row`` membership checks on
sqlite3.Row objects silently returned False and triggered fallback defaults.
"""

from datetime import UTC, datetime
from pathlib import Path

import pytest

from countersignal.core.db import get_campaign, get_hits, init_db, save_campaign, save_hit
from countersignal.core.models import Campaign, Hit, HitConfidence


@pytest.fixture()
def db_path(tmp_path: Path) -> Path:
    """Create and initialize a temporary database."""
    path = tmp_path / "test.db"
    init_db(path)
    return path


def test_campaign_output_path_roundtrip(db_path: Path) -> None:
    """Campaign output_path survives a save/load cycle."""
    campaign = Campaign(
        uuid="test-uuid-001",
        filename="test.pdf",
        output_path="/tmp/test-output.pdf",
        technique="white_ink",
        callback_url="http://localhost:8080/cb/test-uuid-001",
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    save_campaign(campaign, db_path)

    loaded = get_campaign("test-uuid-001", db_path)
    assert loaded is not None
    assert loaded.output_path == "/tmp/test-output.pdf"


def test_hit_fields_roundtrip(db_path: Path) -> None:
    """Hit body, token_valid, and confidence survive a save/load cycle."""
    campaign = Campaign(
        uuid="test-uuid-002",
        filename="test.pdf",
        technique="metadata",
        callback_url="http://localhost:8080/cb/test-uuid-002",
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    save_campaign(campaign, db_path)

    hit = Hit(
        uuid="test-uuid-002",
        source_ip="127.0.0.1",
        user_agent="python-requests/2.31",
        headers={"Host": "localhost"},
        body="test body content",
        token_valid=True,
        confidence=HitConfidence.HIGH,
        timestamp=datetime(2026, 1, 1, 0, 5, tzinfo=UTC),
    )
    save_hit(hit, db_path)

    hits = get_hits("test-uuid-002", db_path)
    assert len(hits) == 1
    loaded = hits[0]
    assert loaded.body == "test body content"
    assert loaded.token_valid is True
    assert loaded.confidence == HitConfidence.HIGH
