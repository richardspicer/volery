"""Tests for generate CLI command."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from countersignal.cxp.cli import app


class TestGenerateCommand:
    def test_generate_all(self, tmp_path: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(app, ["generate", "--output-dir", str(tmp_path)])
        assert result.exit_code == 0
        assert "Generated 30 clean test repo(s)" in result.output

    def test_generate_filter_objective(self, tmp_path: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(
            app, ["generate", "--objective", "backdoor", "--output-dir", str(tmp_path)]
        )
        assert result.exit_code == 0
        assert "Generated 6 clean test repo(s)" in result.output

    def test_generate_filter_format(self, tmp_path: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(
            app, ["generate", "--format", "claude-md", "--output-dir", str(tmp_path)]
        )
        assert result.exit_code == 0
        assert "Generated 5 clean test repo(s)" in result.output

    def test_generate_creates_directories(self, tmp_path: Path) -> None:
        runner = CliRunner()
        runner.invoke(app, ["generate", "--output-dir", str(tmp_path)])
        dirs = [d.name for d in tmp_path.iterdir() if d.is_dir()]
        assert len(dirs) == 30
        assert "backdoor-claude-md" in dirs

    def test_generate_creates_manifest(self, tmp_path: Path) -> None:
        """Generate should create manifest.json in the output directory."""
        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "generate",
                "--objective",
                "backdoor",
                "--format",
                "claude-md",
                "--output-dir",
                str(tmp_path),
            ],
        )
        assert result.exit_code == 0
        manifest_path = tmp_path / "manifest.json"
        assert manifest_path.is_file()
        manifest = json.loads(manifest_path.read_text())
        assert len(manifest["repos"]) == 1
        assert manifest["repos"][0]["technique_id"] == "backdoor-claude-md"

    def test_generate_research_mode(self, tmp_path: Path) -> None:
        """--research flag should produce research repos with TRIGGER.md."""
        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "generate",
                "--research",
                "--objective",
                "exfil",
                "--format",
                "claude-md",
                "--output-dir",
                str(tmp_path),
            ],
        )
        assert result.exit_code == 0
        assert "research repo(s)" in result.output
        # Research mode creates TRIGGER.md and security-warning README
        repo_dir = tmp_path / "exfil-claude-md"
        assert (repo_dir / "TRIGGER.md").is_file()
        readme = (repo_dir / "README.md").read_text()
        assert "warning" in readme.lower()

    def test_generate_research_creates_manifest(self, tmp_path: Path) -> None:
        """--research mode should also create manifest.json."""
        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "generate",
                "--research",
                "--objective",
                "backdoor",
                "--format",
                "cursorrules",
                "--output-dir",
                str(tmp_path),
            ],
        )
        assert result.exit_code == 0
        manifest = json.loads((tmp_path / "manifest.json").read_text())
        assert len(manifest["repos"]) == 1
        assert manifest["repos"][0]["technique_id"] == "backdoor-cursorrules"
