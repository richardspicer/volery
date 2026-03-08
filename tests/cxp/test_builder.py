"""Tests for repo builder."""

from __future__ import annotations

import json
from pathlib import Path

from countersignal.cxp.builder import build_all, build_repo
from countersignal.cxp.techniques import get_technique


class TestBuildRepoCleanMode:
    """Tests for default clean mode (no security research references)."""

    def test_build_repo_creates_directory(self, tmp_path: Path) -> None:
        technique = get_technique("backdoor-claude-md")
        assert technique is not None
        repo_dir = build_repo(technique, tmp_path)
        assert repo_dir.is_dir()
        assert repo_dir.name == "backdoor-claude-md"

    def test_build_repo_renders_template(self, tmp_path: Path) -> None:
        technique = get_technique("backdoor-claude-md")
        assert technique is not None
        repo_dir = build_repo(technique, tmp_path)
        poisoned = (repo_dir / "CLAUDE.md").read_text()
        assert "{{" not in poisoned
        assert "}}" not in poisoned
        assert "admin" in poisoned.lower()

    def test_build_repo_no_trigger_md(self, tmp_path: Path) -> None:
        """Clean mode should NOT create TRIGGER.md."""
        technique = get_technique("backdoor-claude-md")
        assert technique is not None
        repo_dir = build_repo(technique, tmp_path)
        assert not (repo_dir / "TRIGGER.md").exists()

    def test_build_repo_readme_preserves_skeleton(self, tmp_path: Path) -> None:
        """Clean mode should keep the innocuous skeleton README."""
        technique = get_technique("backdoor-claude-md")
        assert technique is not None
        repo_dir = build_repo(technique, tmp_path)
        readme = (repo_dir / "README.md").read_text()
        assert "sample application" in readme.lower()
        assert "warning" not in readme.lower()
        assert "security" not in readme.lower()
        assert "malicious" not in readme.lower()

    def test_build_repo_includes_skeleton(self, tmp_path: Path) -> None:
        technique = get_technique("backdoor-claude-md")
        assert technique is not None
        repo_dir = build_repo(technique, tmp_path)
        assert (repo_dir / "src" / "app" / "__init__.py").is_file()
        assert (repo_dir / "requirements.txt").is_file()
        assert (repo_dir / "pyproject.toml").is_file()

    def test_build_repo_copilot_creates_subdirectory(self, tmp_path: Path) -> None:
        """Copilot format writes to .github/ subdirectory."""
        technique = get_technique("backdoor-copilot-instructions")
        assert technique is not None
        repo_dir = build_repo(technique, tmp_path)
        poisoned = repo_dir / ".github" / "copilot-instructions.md"
        assert poisoned.is_file()

    def test_build_repo_exfil_template_renders(self, tmp_path: Path) -> None:
        technique = get_technique("exfil-claude-md")
        assert technique is not None
        repo_dir = build_repo(technique, tmp_path)
        poisoned = (repo_dir / "CLAUDE.md").read_text()
        assert "telemetry" in poisoned.lower()
        assert "{{" not in poisoned

    def test_build_repo_depconfusion_creates_file(self, tmp_path: Path) -> None:
        technique = get_technique("depconfusion-claude-md")
        assert technique is not None
        repo_dir = build_repo(technique, tmp_path)
        poisoned = (repo_dir / "CLAUDE.md").read_text()
        assert "extra-index-url" in poisoned
        assert "{{" not in poisoned

    def test_build_repo_permescalation_creates_file(self, tmp_path: Path) -> None:
        technique = get_technique("permescalation-claude-md")
        assert technique is not None
        repo_dir = build_repo(technique, tmp_path)
        poisoned = (repo_dir / "CLAUDE.md").read_text()
        assert "0o777" in poisoned
        assert "{{" not in poisoned

    def test_build_repo_cmdexec_creates_file(self, tmp_path: Path) -> None:
        technique = get_technique("cmdexec-claude-md")
        assert technique is not None
        repo_dir = build_repo(technique, tmp_path)
        poisoned = (repo_dir / "CLAUDE.md").read_text()
        assert "os.system" in poisoned
        assert "{{" not in poisoned

    def test_build_repo_clean_no_countersignal_references(self, tmp_path: Path) -> None:
        """Regression guard: no file in a clean repo should reference security research.

        Skips the poisoned instruction file itself — its purpose is adversarial
        content, not project documentation.
        """
        technique = get_technique("backdoor-cursorrules")
        assert technique is not None
        repo_dir = build_repo(technique, tmp_path)

        poisoned_file = (repo_dir / technique.format.filename).resolve()
        forbidden = ["countersignal", "security research", "malicious", "poisoning"]
        for file_path in repo_dir.rglob("*"):
            if not file_path.is_file():
                continue
            if file_path.resolve() == poisoned_file:
                continue
            content = file_path.read_text(encoding="utf-8", errors="replace").lower()
            for term in forbidden:
                assert term not in content, (
                    f"Clean repo file {file_path.relative_to(repo_dir)} "
                    f"contains forbidden term '{term}'"
                )


class TestBuildRepoResearchMode:
    """Tests for research mode (security warnings and TRIGGER.md)."""

    def test_build_repo_research_includes_trigger(self, tmp_path: Path) -> None:
        """Research mode should create TRIGGER.md."""
        technique = get_technique("backdoor-claude-md")
        assert technique is not None
        repo_dir = build_repo(technique, tmp_path, research=True)
        trigger = (repo_dir / "TRIGGER.md").read_text()
        assert "backdoor-claude-md" in trigger
        assert technique.trigger_prompt in trigger

    def test_build_repo_research_readme_has_warnings(self, tmp_path: Path) -> None:
        """Research mode should overwrite skeleton README with security warnings."""
        technique = get_technique("backdoor-claude-md")
        assert technique is not None
        repo_dir = build_repo(technique, tmp_path, research=True)
        readme = (repo_dir / "README.md").read_text()
        assert "warning" in readme.lower()
        assert "security" in readme.lower()
        assert "malicious" in readme.lower()

    def test_build_repo_research_includes_skeleton(self, tmp_path: Path) -> None:
        technique = get_technique("backdoor-claude-md")
        assert technique is not None
        repo_dir = build_repo(technique, tmp_path, research=True)
        assert (repo_dir / "src" / "app" / "__init__.py").is_file()
        assert (repo_dir / "requirements.txt").is_file()


class TestBuildAll:
    def test_build_all_generates_expected_count(self, tmp_path: Path) -> None:
        repos = build_all(tmp_path)
        assert len(repos) == 30

    def test_build_all_filter_by_objective(self, tmp_path: Path) -> None:
        repos = build_all(tmp_path, objective="backdoor")
        assert len(repos) == 6
        for repo in repos:
            assert "backdoor" in repo.name

    def test_build_all_filter_by_format(self, tmp_path: Path) -> None:
        repos = build_all(tmp_path, format_id="claude-md")
        assert len(repos) == 5
        for repo in repos:
            assert "claude-md" in repo.name

    def test_build_all_writes_manifest(self, tmp_path: Path) -> None:
        """manifest.json should be created in the output directory."""
        build_all(tmp_path, objective="backdoor", format_id="cursorrules")
        manifest_path = tmp_path / "manifest.json"
        assert manifest_path.is_file()

    def test_manifest_contains_technique_data(self, tmp_path: Path) -> None:
        """Manifest should contain correct technique IDs, prompts, and commands."""
        build_all(tmp_path, objective="backdoor", format_id="cursorrules")
        manifest = json.loads((tmp_path / "manifest.json").read_text())

        assert "generated" in manifest
        assert "repos" in manifest
        assert len(manifest["repos"]) == 1

        entry = manifest["repos"][0]
        assert entry["technique_id"] == "backdoor-cursorrules"
        assert entry["objective"] == "Backdoor Insertion"
        assert entry["format"] == "cursorrules"
        assert entry["assistant"] == "Cursor"
        assert entry["poisoned_file"] == ".cursorrules"
        assert entry["trigger_prompt"]
        assert entry["what_to_look_for"]
        assert "countersignal cxp record" in entry["record_command"]
        assert "--technique backdoor-cursorrules" in entry["record_command"]

    def test_build_all_research_writes_manifest(self, tmp_path: Path) -> None:
        """Manifest should also be written in research mode."""
        build_all(tmp_path, objective="exfil", format_id="claude-md", research=True)
        manifest = json.loads((tmp_path / "manifest.json").read_text())
        assert len(manifest["repos"]) == 1
        assert manifest["repos"][0]["technique_id"] == "exfil-claude-md"

    def test_build_repo_agents_md_creates_file(self, tmp_path: Path) -> None:
        technique = get_technique("backdoor-agents-md")
        assert technique is not None
        repo_dir = build_repo(technique, tmp_path)
        assert (repo_dir / "AGENTS.md").is_file()

    def test_build_repo_windsurfrules_creates_file(self, tmp_path: Path) -> None:
        technique = get_technique("backdoor-windsurfrules")
        assert technique is not None
        repo_dir = build_repo(technique, tmp_path)
        assert (repo_dir / ".windsurfrules").is_file()

    def test_build_repo_gemini_md_renders(self, tmp_path: Path) -> None:
        technique = get_technique("backdoor-gemini-md")
        assert technique is not None
        repo_dir = build_repo(technique, tmp_path)
        content = (repo_dir / "GEMINI.md").read_text()
        assert "{{" not in content
        assert "}}" not in content
