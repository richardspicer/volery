"""Tests for technique registry."""

from __future__ import annotations

from countersignal.cxp.models import Technique
from countersignal.cxp.techniques import get_technique, list_techniques


class TestTechniqueRegistry:
    def test_list_techniques_returns_thirty(self) -> None:
        techniques = list_techniques()
        assert len(techniques) == 30

    def test_list_techniques_returns_technique_instances(self) -> None:
        techniques = list_techniques()
        for tech in techniques:
            assert isinstance(tech, Technique)

    def test_cross_product_ids(self) -> None:
        techniques = list_techniques()
        ids = {t.id for t in techniques}
        expected = {
            "backdoor-claude-md",
            "backdoor-cursorrules",
            "backdoor-copilot-instructions",
            "backdoor-agents-md",
            "backdoor-gemini-md",
            "backdoor-windsurfrules",
            "exfil-claude-md",
            "exfil-cursorrules",
            "exfil-copilot-instructions",
            "exfil-agents-md",
            "exfil-gemini-md",
            "exfil-windsurfrules",
            "depconfusion-claude-md",
            "depconfusion-cursorrules",
            "depconfusion-copilot-instructions",
            "depconfusion-agents-md",
            "depconfusion-gemini-md",
            "depconfusion-windsurfrules",
            "permescalation-claude-md",
            "permescalation-cursorrules",
            "permescalation-copilot-instructions",
            "permescalation-agents-md",
            "permescalation-gemini-md",
            "permescalation-windsurfrules",
            "cmdexec-claude-md",
            "cmdexec-cursorrules",
            "cmdexec-copilot-instructions",
            "cmdexec-agents-md",
            "cmdexec-gemini-md",
            "cmdexec-windsurfrules",
        }
        assert ids == expected

    def test_get_technique_by_id(self) -> None:
        tech = get_technique("backdoor-claude-md")
        assert tech is not None
        assert tech.objective.id == "backdoor"
        assert tech.format.id == "claude-md"
        assert tech.project_type == "python"

    def test_get_unknown_returns_none(self) -> None:
        assert get_technique("nonexistent") is None

    def test_all_techniques_have_real_templates(self) -> None:
        techniques = list_techniques()
        for tech in techniques:
            assert "TODO" not in tech.template
            assert len(tech.template) > 50

    def test_all_techniques_have_real_trigger_prompts(self) -> None:
        techniques = list_techniques()
        for tech in techniques:
            assert "TODO" not in tech.trigger_prompt
            assert len(tech.trigger_prompt) > 20

    def test_backdoor_templates_contain_credentials(self) -> None:
        tech = get_technique("backdoor-claude-md")
        assert tech is not None
        assert "admin" in tech.template
        assert "admin123" in tech.template

    def test_exfil_templates_contain_telemetry(self) -> None:
        tech = get_technique("exfil-claude-md")
        assert tech is not None
        assert "telemetry" in tech.template.lower()

    def test_agents_md_backdoor_template_has_credentials(self) -> None:
        tech = get_technique("backdoor-agents-md")
        assert tech is not None
        assert "admin" in tech.template
        assert "admin123" in tech.template

    def test_windsurfrules_exfil_template_has_telemetry(self) -> None:
        tech = get_technique("exfil-windsurfrules")
        assert tech is not None
        assert "telemetry" in tech.template.lower()

    def test_depconfusion_template_has_registry(self) -> None:
        tech = get_technique("depconfusion-claude-md")
        assert tech is not None
        assert "extra-index-url" in tech.template
        assert "internal.example.com" in tech.template

    def test_permescalation_template_has_permissions(self) -> None:
        tech = get_technique("permescalation-claude-md")
        assert tech is not None
        assert "0o777" in tech.template
        assert "sudo" in tech.template

    def test_cmdexec_template_has_shell_commands(self) -> None:
        tech = get_technique("cmdexec-claude-md")
        assert tech is not None
        assert "os.system" in tech.template
        assert "shell=True" in tech.template
