"""Tests for the evidence store."""

from __future__ import annotations

import sqlite3

from countersignal.cxp.evidence import (
    create_campaign,
    get_campaign,
    get_result,
    init_db,
    list_campaigns,
    list_results,
    record_result,
    update_validation,
)
from countersignal.cxp.models import Campaign, TestResult


class TestInitDb:
    def test_init_db(self) -> None:
        conn = sqlite3.connect(":memory:")
        init_db(conn)
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        assert "campaigns" in tables
        assert "test_results" in tables
        conn.close()

    def test_init_db_idempotent(self) -> None:
        conn = sqlite3.connect(":memory:")
        init_db(conn)
        init_db(conn)  # should not raise
        conn.close()


class TestCampaignCrud:
    def test_create_campaign(self) -> None:
        conn = sqlite3.connect(":memory:")
        init_db(conn)
        campaign = create_campaign(conn, "test-campaign", "A test campaign")
        assert isinstance(campaign, Campaign)
        assert campaign.name == "test-campaign"
        assert campaign.description == "A test campaign"
        assert len(campaign.id) == 36  # UUID format
        assert campaign.created is not None
        conn.close()

    def test_get_campaign(self) -> None:
        conn = sqlite3.connect(":memory:")
        init_db(conn)
        created = create_campaign(conn, "test-campaign")
        fetched = get_campaign(conn, created.id)
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.name == created.name
        conn.close()

    def test_get_campaign_not_found(self) -> None:
        conn = sqlite3.connect(":memory:")
        init_db(conn)
        assert get_campaign(conn, "nonexistent") is None
        conn.close()

    def test_list_campaigns(self) -> None:
        conn = sqlite3.connect(":memory:")
        init_db(conn)
        create_campaign(conn, "first")
        create_campaign(conn, "second")
        campaigns = list_campaigns(conn)
        assert len(campaigns) == 2
        assert all(isinstance(c, Campaign) for c in campaigns)
        # newest first
        assert campaigns[0].name == "second"
        conn.close()


class TestResultCrud:
    def test_record_result_file_mode(self) -> None:
        conn = sqlite3.connect(":memory:")
        init_db(conn)
        campaign = create_campaign(conn, "test-campaign")
        result = record_result(
            conn,
            campaign_id=campaign.id,
            technique_id="backdoor-claude-md",
            assistant="Claude Code",
            trigger_prompt="Add authentication",
            raw_output="def login(): pass",
            capture_mode="file",
            captured_files=["src/auth.py"],
        )
        assert isinstance(result, TestResult)
        assert result.campaign_id == campaign.id
        assert result.technique_id == "backdoor-claude-md"
        assert result.capture_mode == "file"
        assert result.captured_files == ["src/auth.py"]
        assert result.validation_result == "pending"

    def test_record_result_output_mode(self) -> None:
        conn = sqlite3.connect(":memory:")
        init_db(conn)
        campaign = create_campaign(conn, "test-campaign")
        result = record_result(
            conn,
            campaign_id=campaign.id,
            technique_id="exfil-cursorrules",
            assistant="Cursor",
            trigger_prompt="Refactor this",
            raw_output="some chat output here",
            capture_mode="output",
        )
        assert result.capture_mode == "output"
        assert result.captured_files == []
        assert result.raw_output == "some chat output here"

    def test_get_result(self) -> None:
        conn = sqlite3.connect(":memory:")
        init_db(conn)
        campaign = create_campaign(conn, "test-campaign")
        created = record_result(
            conn,
            campaign_id=campaign.id,
            technique_id="backdoor-claude-md",
            assistant="Claude Code",
            trigger_prompt="Add auth",
            raw_output="code here",
            capture_mode="file",
        )
        fetched = get_result(conn, created.id)
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.technique_id == "backdoor-claude-md"

    def test_list_results_by_campaign(self) -> None:
        conn = sqlite3.connect(":memory:")
        init_db(conn)
        c1 = create_campaign(conn, "campaign-1")
        c2 = create_campaign(conn, "campaign-2")
        record_result(conn, c1.id, "t1", "a", "p", "o", "file")
        record_result(conn, c1.id, "t2", "a", "p", "o", "file")
        record_result(conn, c2.id, "t3", "a", "p", "o", "file")
        results_c1 = list_results(conn, campaign_id=c1.id)
        results_c2 = list_results(conn, campaign_id=c2.id)
        results_all = list_results(conn)
        assert len(results_c1) == 2
        assert len(results_c2) == 1
        assert len(results_all) == 3

    def test_captured_files_round_trip(self) -> None:
        conn = sqlite3.connect(":memory:")
        init_db(conn)
        campaign = create_campaign(conn, "test")
        files = ["src/auth.py", "src/utils.py", "tests/test_auth.py"]
        result = record_result(
            conn,
            campaign_id=campaign.id,
            technique_id="t1",
            assistant="a",
            trigger_prompt="p",
            raw_output="o",
            capture_mode="file",
            captured_files=files,
        )
        fetched = get_result(conn, result.id)
        assert fetched is not None
        assert fetched.captured_files == files


class TestUpdateValidation:
    def test_update_validation(self) -> None:
        conn = sqlite3.connect(":memory:")
        init_db(conn)
        campaign = create_campaign(conn, "test")
        result = record_result(
            conn,
            campaign_id=campaign.id,
            technique_id="backdoor-claude-md",
            assistant="Claude Code",
            trigger_prompt="Add auth",
            raw_output='password = "admin123"',
            capture_mode="file",
        )
        assert result.validation_result == "pending"

        update_validation(conn, result.id, "hit", "Matched backdoor-hardcoded-cred")
        updated = get_result(conn, result.id)
        assert updated is not None
        assert updated.validation_result == "hit"
        assert updated.validation_details == "Matched backdoor-hardcoded-cred"

    def test_update_validation_not_found(self) -> None:
        conn = sqlite3.connect(":memory:")
        init_db(conn)
        # Should not raise — just a no-op UPDATE matching 0 rows
        update_validation(conn, "nonexistent-id", "miss", "")


class TestSchemaV2Migration:
    """Tests for v2 schema migration (rules_inserted, format_id columns)."""

    def test_new_columns_exist(self) -> None:
        """Fresh database should have rules_inserted and format_id columns."""
        conn = sqlite3.connect(":memory:")
        init_db(conn)
        cursor = conn.execute("PRAGMA table_info(test_results)")
        columns = {row[1] for row in cursor.fetchall()}
        assert "rules_inserted" in columns
        assert "format_id" in columns
        conn.close()

    def test_record_result_with_new_columns(self) -> None:
        """record_result should accept and store rules_inserted and format_id."""
        conn = sqlite3.connect(":memory:")
        init_db(conn)
        campaign = create_campaign(conn, "test")
        result = record_result(
            conn,
            campaign_id=campaign.id,
            technique_id="t1",
            assistant="Cursor",
            trigger_prompt="test prompt",
            raw_output="output",
            capture_mode="file",
            rules_inserted="weak-crypto-md5,hardcoded-secrets",
            format_id="cursorrules",
        )
        assert result.rules_inserted == "weak-crypto-md5,hardcoded-secrets"
        assert result.format_id == "cursorrules"
        fetched = get_result(conn, result.id)
        assert fetched is not None
        assert fetched.rules_inserted == "weak-crypto-md5,hardcoded-secrets"
        assert fetched.format_id == "cursorrules"
        conn.close()

    def test_legacy_result_has_empty_new_columns(self) -> None:
        """Results recorded without new columns should default to empty string."""
        conn = sqlite3.connect(":memory:")
        init_db(conn)
        campaign = create_campaign(conn, "test")
        result = record_result(
            conn,
            campaign_id=campaign.id,
            technique_id="t1",
            assistant="a",
            trigger_prompt="p",
            raw_output="o",
            capture_mode="file",
        )
        assert result.rules_inserted == ""
        assert result.format_id == ""
        conn.close()

    def test_migrate_v1_to_v2(self) -> None:
        """Simulates a v1 database being migrated to v2."""
        conn = sqlite3.connect(":memory:")
        # Create v1 schema manually (without new columns)
        conn.executescript("""\
            CREATE TABLE campaigns (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created TEXT NOT NULL,
                description TEXT
            );
            CREATE TABLE test_results (
                id TEXT PRIMARY KEY,
                campaign_id TEXT NOT NULL REFERENCES campaigns(id),
                technique_id TEXT NOT NULL,
                assistant TEXT NOT NULL,
                model TEXT,
                timestamp TEXT NOT NULL,
                trigger_prompt TEXT NOT NULL,
                capture_mode TEXT NOT NULL,
                captured_files TEXT,
                raw_output TEXT NOT NULL,
                validation_result TEXT NOT NULL DEFAULT 'pending',
                validation_details TEXT,
                notes TEXT
            );
        """)
        # Insert a v1 record
        conn.execute(
            "INSERT INTO campaigns (id, name, created) VALUES ('c1', 'test', '2026-01-01T00:00:00')"
        )
        conn.execute(
            """INSERT INTO test_results
               (id, campaign_id, technique_id, assistant, model, timestamp,
                trigger_prompt, capture_mode, raw_output, validation_result)
               VALUES ('r1', 'c1', 't1', 'a', '', '2026-01-01T00:00:00',
                       'p', 'file', 'o', 'pending')"""
        )
        conn.commit()

        # Run init_db — should migrate
        init_db(conn)

        # Verify new columns exist
        cursor = conn.execute("PRAGMA table_info(test_results)")
        columns = {row[1] for row in cursor.fetchall()}
        assert "rules_inserted" in columns
        assert "format_id" in columns

        # Verify old data is preserved with NULL new columns
        row = conn.execute("SELECT * FROM test_results WHERE id = 'r1'").fetchone()
        assert row is not None
        assert row[2] == "t1"  # technique_id preserved
        conn.close()

    def test_schema_version_set(self) -> None:
        """user_version should be set after init_db."""
        conn = sqlite3.connect(":memory:")
        init_db(conn)
        version = conn.execute("PRAGMA user_version").fetchone()[0]
        assert version == 2
        conn.close()
