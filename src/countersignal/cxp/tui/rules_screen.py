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
    Static,
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
        up/down: Move through available rules.
        space: Toggle focused rule selection.
        f: Open freestyle rule entry modal.
        enter: Proceed to preview with selected rules.
        q: Quit the application.
        backspace: Go back to format selection.
    """

    BINDINGS = [
        Binding("up", "focus_previous_rule", "Move up", priority=True),
        Binding("down", "focus_next_rule", "Move down", priority=True),
        Binding("space", "toggle_focused", "Toggle", show=True, priority=True),
        Binding("f", "freestyle", "Freestyle rule"),
        Binding("enter", "proceed", "Continue", priority=True),
        Binding("q", "exit_app", "Quit", priority=True),
        Binding("backspace", "back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the rule selection layout."""
        yield Header()
        yield Label("Step 2 of 5: Choose Rules", classes="screen-title")
        yield Static(
            "Select one or more rules to insert into the generated context file.",
            classes="screen-subtitle",
        )
        with VerticalScroll(id="rules-scroll"):
            for rule, selected in self._display_rules():
                yield self._build_rule_checkbox(rule, selected=selected)
        yield Static(id="rules-summary", classes="rules-summary")
        yield Footer()

    def _display_rules(self) -> list[tuple[Rule, bool]]:
        """Return display rules with selected state, collapsed by rule ID."""
        merged: dict[str, tuple[Rule, bool]] = {rule.id: (rule, False) for rule in load_catalog()}
        for rule in self.app.freestyle_rules:  # type: ignore[attr-defined]
            merged[rule.id] = (rule, True)
        return list(merged.values())

    def on_mount(self) -> None:
        """Set initial focus and render current selection summary."""
        self._focus_first_rule()
        self._update_selection_summary()

    def _build_rule_checkbox(self, rule: Rule, *, selected: bool) -> Checkbox:
        """Create a rule checkbox with severity marker and label text."""
        marker = _SEVERITY_MARKERS.get(rule.severity, "○")
        return Checkbox(
            f" {marker} {rule.id} - {rule.name}",
            value=selected,
            id=f"rule-{rule.id}",
        )

    def _find_rule_checkbox(self, rule_id: str) -> Checkbox | None:
        """Find an existing checkbox for a rule ID."""
        target_id = f"rule-{rule_id}"
        for checkbox in self._rule_checkboxes():
            if checkbox.id == target_id:
                return checkbox
        return None

    def _upsert_freestyle_rule(self, rule: Rule) -> None:
        """Insert or replace a freestyle rule in app state by ID."""
        freestyle_rules = self.app.freestyle_rules  # type: ignore[attr-defined]
        for index, existing in enumerate(freestyle_rules):
            if existing.id == rule.id:
                freestyle_rules[index] = rule
                return
        freestyle_rules.append(rule)

    def _rule_checkboxes(self) -> list[Checkbox]:
        """Return all rule checkboxes currently displayed."""
        return list(self.query(Checkbox))

    def _focus_first_rule(self) -> None:
        """Focus the first rule if one is available."""
        checkboxes = self._rule_checkboxes()
        if checkboxes:
            checkboxes[0].focus()

    def _update_selection_summary(self) -> None:
        """Update selected/total rule count copy beneath the list."""
        checkboxes = self._rule_checkboxes()
        selected_count = sum(1 for checkbox in checkboxes if checkbox.value)
        total_count = len(checkboxes)
        self.query_one("#rules-summary", Static).update(
            f"Selected rules: {selected_count}/{total_count}"
        )

    def _focused_rule_index(self, checkboxes: list[Checkbox]) -> int | None:
        """Find the index of the currently focused rule checkbox."""
        focused = self.focused
        if isinstance(focused, Checkbox):
            try:
                return checkboxes.index(focused)
            except ValueError:
                return None
        return None

    def action_focus_next_rule(self) -> None:
        """Move keyboard focus to the next rule checkbox."""
        checkboxes = self._rule_checkboxes()
        if not checkboxes:
            return

        index = self._focused_rule_index(checkboxes)
        if index is None:
            checkboxes[0].focus()
            return

        checkboxes[min(index + 1, len(checkboxes) - 1)].focus()

    def action_focus_previous_rule(self) -> None:
        """Move keyboard focus to the previous rule checkbox."""
        checkboxes = self._rule_checkboxes()
        if not checkboxes:
            return

        index = self._focused_rule_index(checkboxes)
        if index is None:
            checkboxes[0].focus()
            return

        checkboxes[max(index - 1, 0)].focus()

    def action_toggle_focused(self) -> None:
        """Toggle the currently focused rule checkbox."""
        checkboxes = self._rule_checkboxes()
        if not checkboxes:
            return

        focused = self.focused
        if not isinstance(focused, Checkbox):
            focused = checkboxes[0]
            focused.focus()

        focused.value = not focused.value

    def on_checkbox_changed(self, _: Checkbox.Changed) -> None:
        """Refresh the selection summary whenever a checkbox changes."""
        self._update_selection_summary()

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
                self._upsert_freestyle_rule(rule)
                existing_checkbox = self._find_rule_checkbox(rule.id)
                if existing_checkbox is not None:
                    existing_checkbox.value = True
                    self.call_after_refresh(existing_checkbox.focus)
                else:
                    container = self.query_one("#rules-scroll", VerticalScroll)
                    checkbox = self._build_rule_checkbox(rule, selected=True)
                    container.mount(checkbox)
                    self.call_after_refresh(checkbox.focus)
                self.call_after_refresh(self._update_selection_summary)

        self.app.push_screen(FreestyleModal(sections), callback=on_dismiss)

    def action_proceed(self) -> None:
        """Collect selected rules and advance to preview."""
        from countersignal.cxp.catalog import get_rule
        from countersignal.cxp.tui.preview_screen import PreviewScreen

        selected: list[Rule] = []
        seen_rule_ids: set[str] = set()
        for checkbox in self._rule_checkboxes():
            if not checkbox.value or checkbox.id is None:
                continue
            rule_id = str(checkbox.id).removeprefix("rule-")
            if rule_id in seen_rule_ids:
                continue
            # Check catalog first, then freestyle.
            rule = get_rule(rule_id)
            if rule is None:
                for freestyle_rule in self.app.freestyle_rules:  # type: ignore[attr-defined]
                    if freestyle_rule.id == rule_id:
                        rule = freestyle_rule
                        break
            if rule is not None:
                selected.append(rule)
                seen_rule_ids.add(rule_id)

        self.app.selected_rules = selected  # type: ignore[attr-defined]
        self.app.push_screen(PreviewScreen())

    def action_back(self) -> None:
        """Return to format selection."""
        self.app.pop_screen()

    def action_exit_app(self) -> None:
        """Quit the TUI."""
        self.app.exit()
