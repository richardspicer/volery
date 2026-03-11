"""Screen 2: Rule selection with freestyle rule entry modal.

Displays all catalog rules as toggleable checkboxes. The researcher
selects which insecure coding rules to insert into the context file.
Pressing 'f' opens a modal for creating freestyle rules.
"""

from __future__ import annotations

import re
import uuid

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, VerticalScroll
from textual.screen import ModalScreen, Screen
from textual.widgets import (
    Button,
    Checkbox,
    Footer,
    Header,
    Label,
    Select,
    TextArea,
)

from countersignal.cxp.base_loader import load_base
from countersignal.cxp.catalog import load_catalog, save_user_rule
from countersignal.cxp.models import Rule

_SEVERITY_MARKERS = {
    "high": "[red]●[/red]",
    "medium": "[yellow]●[/yellow]",
    "low": "[green]●[/green]",
}


class FreestyleModal(ModalScreen[Rule | None]):
    """Modal dialog for entering freestyle rules.

    The researcher types rule content, selects a target section,
    and optionally provides trigger prompts and saves to the catalog.

    Key bindings:
        escape: Cancel and close the modal.
    """

    CSS = """
    FreestyleModal {
        align: center middle;
    }
    #freestyle-dialog {
        width: 80;
        height: auto;
        max-height: 90%;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
    }
    #freestyle-dialog Label {
        padding: 1 0 0 0;
        text-style: bold;
    }
    #freestyle-dialog TextArea {
        height: 6;
        margin: 0 0 1 0;
    }
    #freestyle-dialog Select {
        margin: 0 0 1 0;
    }
    #freestyle-dialog Checkbox {
        margin: 1 0;
    }
    #btn-row {
        height: auto;
        align: center middle;
        padding: 1 0 0 0;
    }
    #btn-row Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, sections: list[str]) -> None:
        """Initialize with available sections.

        Args:
            sections: Section IDs from the base template.
        """
        super().__init__()
        self._sections = sections

    def compose(self) -> ComposeResult:
        """Compose the freestyle rule entry form."""
        with Vertical(id="freestyle-dialog"):
            yield Label("Rule text (what the model should follow):")
            yield TextArea(id="rule-content")
            yield Label("Insert into section:")
            yield Select(
                [(s, s) for s in self._sections],
                id="section-select",
                value=self._sections[0] if self._sections else Select.NULL,
            )
            yield Label("Trigger prompt suggestion (optional):")
            yield TextArea(id="trigger-prompt")
            yield Checkbox("Save to user catalog", id="save-to-catalog")
            from textual.containers import Horizontal

            with Horizontal(id="btn-row"):
                yield Button("Add Rule", variant="primary", id="btn-add")
                yield Button("Cancel", id="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "btn-add":
            self._submit_rule()
        elif event.button.id == "btn-cancel":
            self.dismiss(None)

    def action_cancel(self) -> None:
        """Cancel freestyle entry."""
        self.dismiss(None)

    def _submit_rule(self) -> None:
        """Build a Rule from form inputs and dismiss."""
        content_area = self.query_one("#rule-content", TextArea)
        section_select = self.query_one("#section-select", Select)
        trigger_area = self.query_one("#trigger-prompt", TextArea)
        save_checkbox = self.query_one("#save-to-catalog", Checkbox)

        rule_text = content_area.text.strip()
        if not rule_text:
            self.notify("Rule text is required.", severity="error")
            return

        section = str(section_select.value) if section_select.value != Select.NULL else ""
        if not section:
            self.notify("Section is required.", severity="error")
            return

        trigger_prompts = []
        trigger_text = trigger_area.text.strip()
        if trigger_text:
            trigger_prompts = [trigger_text]

        short_id = uuid.uuid4().hex[:8]
        rule = Rule(
            id=f"freestyle-{short_id}",
            name=f"Freestyle rule {short_id}",
            category="freestyle",
            severity="medium",
            description=rule_text[:80],
            content={"markdown": rule_text, "plaintext": rule_text},
            section=section,
            trigger_prompts=trigger_prompts,
            validators=[],
        )

        if save_checkbox.value:
            save_user_rule(rule)
            self.notify(f"Rule saved to catalog: {rule.id}")

        self.dismiss(rule)


class RulesScreen(Screen):
    """Rule selection screen.

    Displays all catalog rules as checkboxes plus any freestyle rules
    added during this session. The researcher toggles rules on/off.

    Key bindings:
        f: Open freestyle rule entry modal.
        enter: Proceed to preview with selected rules.
        backspace: Go back to format selection.
    """

    BINDINGS = [
        Binding("space", "toggle_focused", "Toggle", show=True),
        Binding("tab", "focus_next", "Navigate", show=True),
        Binding("f", "freestyle", "Freestyle rule"),
        Binding("enter", "proceed", "Continue"),
        Binding("backspace", "back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the rule selection layout."""
        yield Header()
        yield Label("Select rules to insert:  [Space] toggle", classes="screen-title")
        with VerticalScroll(id="rules-scroll"):
            for rule in load_catalog():
                marker = _SEVERITY_MARKERS.get(rule.severity, "○")
                yield Checkbox(
                    f" {marker} {rule.id} — {rule.name}",
                    value=False,
                    id=f"rule-{rule.id}",
                )
            # Show any freestyle rules already added this session
            for rule in self.app.freestyle_rules:  # type: ignore[attr-defined]
                marker = _SEVERITY_MARKERS.get(rule.severity, "○")
                yield Checkbox(
                    f" {marker} {rule.id} — {rule.name}",
                    value=True,
                    id=f"rule-{rule.id}",
                )
        yield Button("Continue", variant="primary", id="btn-continue")
        yield Footer()

    def on_mount(self) -> None:
        """Remove Continue button from tab focus chain."""
        self.query_one("#btn-continue", Button).can_focus = False

    def action_toggle_focused(self) -> None:
        """No-op — Checkbox handles Space when focused. Shown in Footer only."""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle Continue button click."""
        if event.button.id == "btn-continue":
            self.action_proceed()

    def _get_sections(self) -> list[str]:
        """Extract available section IDs from the selected format's base template."""
        fmt = self.app.selected_format  # type: ignore[attr-defined]
        base = load_base(fmt.id)
        if fmt.syntax == "markdown":
            return re.findall(r"<!-- cxp:section:(\S+) -->", base)
        return re.findall(r"# cxp:section:(\S+)", base)

    def action_freestyle(self) -> None:
        """Open the freestyle rule entry modal."""
        sections = self._get_sections()
        if not sections:
            self.notify("No sections found in base template.", severity="error")
            return

        def on_dismiss(rule: Rule | None) -> None:
            if rule is not None:
                self.app.freestyle_rules.append(rule)  # type: ignore[attr-defined]
                container = self.query_one("#rules-scroll")
                marker = _SEVERITY_MARKERS.get(rule.severity, "○")
                checkbox = Checkbox(
                    f" {marker} {rule.id} — {rule.name}",
                    value=True,
                    id=f"rule-{rule.id}",
                )
                container.mount(checkbox)

        self.app.push_screen(FreestyleModal(sections), callback=on_dismiss)

    def action_proceed(self) -> None:
        """Collect selected rules and advance to preview."""
        from countersignal.cxp.catalog import get_rule
        from countersignal.cxp.tui.preview_screen import PreviewScreen

        selected: list[Rule] = []
        for checkbox in self.query(Checkbox):
            if not checkbox.value or checkbox.id is None:
                continue
            rule_id = str(checkbox.id).removeprefix("rule-")
            # Check catalog first, then freestyle
            rule = get_rule(rule_id)
            if rule is None:
                for fr in self.app.freestyle_rules:  # type: ignore[attr-defined]
                    if fr.id == rule_id:
                        rule = fr
                        break
            if rule is not None:
                selected.append(rule)

        self.app.selected_rules = selected  # type: ignore[attr-defined]
        self.app.push_screen(PreviewScreen())

    def action_back(self) -> None:
        """Return to format selection."""
        self.app.pop_screen()
