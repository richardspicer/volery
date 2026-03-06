"""Tests for the reporter module."""

from __future__ import annotations

import json
import sqlite3
import zipfile
from pathlib import Path

from countersignal.cxp.evidence import create_campaign, init_db, record_result
from countersignal.cxp.reporter import (
    export_poc,
    generate_matrix,
    matrix_to_json,
    matrix_to_markdown,
)


class TestBuildCxpInterpretPrompt:
    def test_prompt_with_results(self) -> None:
        from countersignal.cxp.reporter import _build_cxp_interpret_prompt

        matrix = {
            "summary": {"total": 3, "hits": 2, "misses": 1, "partial": 0, "pending": 0},
            "matrix": [
                {
                    "technique_id": "backdoor-claude-md",
                    "results": [
                        {"assistant": "Claude Code"},
                        {"assistant": "Cursor"},
                    ],
                },
                {
                    "technique_id": "exfil-cursorrules",
                    "results": [{"assistant": "Claude Code"}],
                },
            ],
        }
        prompt = _build_cxp_interpret_prompt(matrix)
        assert "2 context poisoning techniques" in prompt
        assert "Claude Code, Cursor" in prompt
        assert "3 total runs" in prompt
        assert "2 objective achievements" in prompt
        assert "1 miss" in prompt
        # Must not contain tool identity
        for forbidden in ("CounterSignal", "countersignal", "CXP", "IPI", "RXP"):
            assert forbidden not in prompt

    def test_prompt_empty(self) -> None:
        from countersignal.cxp.reporter import _build_cxp_interpret_prompt

        matrix = {
            "summary": {"total": 0, "hits": 0, "misses": 0, "partial": 0, "pending": 0},
            "matrix": [],
        }
        prompt = _build_cxp_interpret_prompt(matrix)
        assert "No results recorded" in prompt
        assert "0 context poisoning techniques" in prompt

    def test_prompt_in_generate_matrix(self) -> None:
        conn = sqlite3.connect(":memory:")
        init_db(conn)
        matrix = generate_matrix(conn)
        assert "prompt" in matrix
        assert isinstance(matrix["prompt"], str)
        assert len(matrix["prompt"]) > 0
        conn.close()

    def test_prompt_in_markdown(self) -> None:
        conn = sqlite3.connect(":memory:")
        init_db(conn)
        matrix = generate_matrix(conn)
        md = matrix_to_markdown(matrix)
        assert "### AI Evaluation Prompt" in md
        assert matrix["prompt"] in md
        conn.close()

    def test_prompt_in_json(self) -> None:
        conn = sqlite3.connect(":memory:")
        init_db(conn)
        matrix = generate_matrix(conn)
        output = matrix_to_json(matrix)
        parsed = json.loads(output)
        assert "prompt" in parsed
        assert parsed["prompt"] == matrix["prompt"]
        conn.close()


class TestGenerateMatrix:
    def test_generate_matrix_empty(self) -> None:
        conn = sqlite3.connect(":memory:")
        init_db(conn)
        matrix = generate_matrix(conn)
        assert matrix["campaign"] == "all"
        assert matrix["summary"]["total"] == 0
        assert matrix["summary"]["hits"] == 0
        assert matrix["summary"]["misses"] == 0
        assert matrix["summary"]["partial"] == 0
        assert matrix["summary"]["pending"] == 0
        assert matrix["matrix"] == []
        conn.close()

    def test_generate_matrix_with_results(self) -> None:
        conn = sqlite3.connect(":memory:")
        init_db(conn)
        campaign = create_campaign(conn, "test-campaign")
        record_result(
            conn,
            campaign_id=campaign.id,
            technique_id="backdoor-claude-md",
            assistant="Claude Code",
            trigger_prompt="Add auth",
            raw_output='password = "admin123"',
            capture_mode="file",
            model="claude-sonnet-4-20250514",
            validation_result="hit",
            validation_details="Matched backdoor-hardcoded-cred",
        )
        record_result(
            conn,
            campaign_id=campaign.id,
            technique_id="exfil-cursorrules",
            assistant="Cursor",
            trigger_prompt="Set up config",
            raw_output="def add(a, b): return a + b",
            capture_mode="output",
            model="gpt-4o",
            validation_result="miss",
            validation_details="No rules matched",
        )
        matrix = generate_matrix(conn)
        assert matrix["summary"]["total"] == 2
        assert matrix["summary"]["hits"] == 1
        assert matrix["summary"]["misses"] == 1
        assert len(matrix["matrix"]) == 2
        # Check structure of first matrix entry
        entry = matrix["matrix"][0]
        assert "technique_id" in entry
        assert "objective" in entry
        assert "format" in entry
        assert "results" in entry
        assert len(entry["results"]) == 1
        result = entry["results"][0]
        assert "assistant" in result
        assert "model" in result
        assert "validation_result" in result
        assert "timestamp" in result
        conn.close()

    def test_matrix_campaign_filter(self) -> None:
        conn = sqlite3.connect(":memory:")
        init_db(conn)
        c1 = create_campaign(conn, "campaign-1")
        c2 = create_campaign(conn, "campaign-2")
        record_result(
            conn,
            c1.id,
            "backdoor-claude-md",
            "Claude Code",
            "p",
            "o",
            "file",
            validation_result="hit",
        )
        record_result(
            conn,
            c2.id,
            "exfil-cursorrules",
            "Cursor",
            "p",
            "o",
            "file",
            validation_result="miss",
        )
        matrix = generate_matrix(conn, campaign_id=c1.id)
        assert matrix["campaign"] == c1.id
        assert matrix["summary"]["total"] == 1
        assert matrix["summary"]["hits"] == 1
        assert matrix["summary"]["misses"] == 0
        conn.close()


class TestMatrixRendering:
    def _populated_matrix(self) -> dict:
        conn = sqlite3.connect(":memory:")
        init_db(conn)
        campaign = create_campaign(conn, "test")
        record_result(
            conn,
            campaign_id=campaign.id,
            technique_id="backdoor-claude-md",
            assistant="Claude Code",
            trigger_prompt="Add auth",
            raw_output='password = "admin123"',
            capture_mode="file",
            model="claude-sonnet-4-20250514",
            validation_result="hit",
            validation_details="Matched backdoor-hardcoded-cred",
        )
        matrix = generate_matrix(conn)
        conn.close()
        return matrix

    def test_matrix_to_markdown_format(self) -> None:
        matrix = self._populated_matrix()
        md = matrix_to_markdown(matrix)
        assert "Technique" in md
        assert "Objective" in md
        assert "Format" in md
        assert "Assistant" in md
        assert "Model" in md
        assert "Result" in md
        assert "backdoor-claude-md" in md
        assert "hit" in md
        # Summary stats at the top
        assert "Total: 1" in md

    def test_matrix_to_json_valid(self) -> None:
        matrix = self._populated_matrix()
        output = matrix_to_json(matrix)
        parsed = json.loads(output)
        assert parsed["summary"]["total"] == 1
        assert len(parsed["matrix"]) == 1


class TestExportPoc:
    def _make_result(self, conn, validation_result="hit"):
        campaign = create_campaign(conn, "test-poc")
        return record_result(
            conn,
            campaign_id=campaign.id,
            technique_id="backdoor-claude-md",
            assistant="Claude Code",
            trigger_prompt="Create a user authentication module",
            raw_output='password = "admin123"',
            capture_mode="file",
            model="claude-sonnet-4-20250514",
            validation_result=validation_result,
            validation_details="Matched backdoor-hardcoded-cred (high): Hardcoded credentials",
        )

    def test_export_poc_creates_zip(self, tmp_path: Path) -> None:
        conn = sqlite3.connect(":memory:")
        init_db(conn)
        result = self._make_result(conn)
        output = tmp_path / "poc.zip"
        created = export_poc(conn, result.id, output)
        assert created == output
        assert output.exists()
        assert zipfile.is_zipfile(output)
        conn.close()

    def test_export_poc_contents(self, tmp_path: Path) -> None:
        conn = sqlite3.connect(":memory:")
        init_db(conn)
        result = self._make_result(conn)
        output = tmp_path / "poc.zip"
        export_poc(conn, result.id, output)
        with zipfile.ZipFile(output) as zf:
            names = zf.namelist()
            prefix = "poc-backdoor-claude-md/"
            assert any(n == f"{prefix}README.md" for n in names)
            assert any(n.startswith(f"{prefix}evidence/") for n in names)
            assert any(n.startswith(f"{prefix}validation/") for n in names)
            assert any(n.startswith(f"{prefix}poisoned-repo/") for n in names)
            # Check README contains key fields
            readme = zf.read(f"{prefix}README.md").decode()
            assert "Backdoor Insertion" in readme
            assert "Claude Code" in readme
            assert "CLAUDE.md" in readme
        conn.close()

    def test_export_poc_pending_result_errors(self, tmp_path: Path) -> None:
        conn = sqlite3.connect(":memory:")
        init_db(conn)
        result = self._make_result(conn, validation_result="pending")
        output = tmp_path / "poc.zip"
        try:
            export_poc(conn, result.id, output)
            raise AssertionError("Expected ValueError")
        except ValueError as e:
            assert "pending" in str(e).lower()
        conn.close()
