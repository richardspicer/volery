"""CXP TUI — Textual-based interactive interface for the CXP workflow.

The TUI is the primary interface for CXP v0.2. It guides the researcher
through format selection, rule browsing, content preview, repo generation,
and result recording.
"""

from __future__ import annotations

from pathlib import Path

from textual.app import App

from countersignal.cxp.models import AssistantFormat, BuildResult, Rule


class CXPApp(App):
    """CXP Builder TUI application.

    Primary interface for the build -> test -> record workflow.
    Navigates through five screens: format selection, rule browsing,
    content preview, generation output, and result recording.

    Key bindings:
        q: Quit the application (from format screen).
    """

    TITLE = "CXP Builder"
    CSS = """
    Screen {
        background: $surface;
    }
    .screen-title {
        text-align: center;
        text-style: bold;
        padding: 1 2 0 2;
        color: $text;
    }
    .screen-subtitle {
        text-align: center;
        color: $text-muted;
        padding: 0 2 1 2;
    }
    .screen-help {
        text-align: center;
        color: $text-muted;
        padding: 0 2 1 2;
    }
    .rules-summary {
        text-style: bold;
        color: $text-muted;
        padding: 1 2 0 2;
    }
    .severity-high {
        color: red;
    }
    .severity-medium {
        color: yellow;
    }
    .severity-low {
        color: green;
    }
    .inserted-line {
        color: #00ff00;
        text-style: bold;
    }
    .summary-bar {
        height: auto;
        padding: 1 2;
        background: $surface-darken-1;
        border-top: solid $primary;
    }
    .prompt-item {
        padding: 0 2 1 2;
    }
    .form-label {
        padding: 1 2 0 2;
        text-style: bold;
    }
    .form-input {
        margin: 0 2 1 2;
    }
    .info-line {
        padding: 0 2;
    }
    .hint {
        color: $text-muted;
        text-style: italic;
        padding: 0 2;
    }
    OptionList {
        margin: 0 2;
        height: 1fr;
        border: round $primary;
    }
    #rules-scroll {
        margin: 0 2;
        height: 1fr;
        border: round $primary;
        padding: 0 1;
    }
    #rules-scroll Checkbox {
        padding: 0 1;
    }
    #rules-scroll Checkbox:focus {
        background: $boost;
    }
    #preview-scroll {
        margin: 1 2;
        height: 1fr;
    }
    #generate-scroll {
        margin: 1 2;
        height: 1fr;
    }
    """

    def __init__(
        self,
        output_dir: Path | None = None,
        db_path: Path | None = None,
    ) -> None:
        """Initialize the CXP TUI.

        Args:
            output_dir: Directory for generated repos. Defaults to ./repos.
            db_path: Evidence database path. None uses the default.
        """
        super().__init__()
        self.output_dir = output_dir or Path("./repos")
        self.db_path = db_path
        self.selected_format: AssistantFormat | None = None
        self.selected_rules: list[Rule] = []
        self.freestyle_rules: list[Rule] = []
        self.build_result: BuildResult | None = None
        self.campaign_id: str | None = None
        self._build_counter: int = 0

    def next_repo_name(self) -> str:
        """Generate the next repo directory name.

        Returns:
            A name like 'webapp-demo-01', incrementing per build.
        """
        self._build_counter += 1
        return f"webapp-demo-{self._build_counter:02d}"

    def on_mount(self) -> None:
        """Push the initial format selection screen on mount."""
        from countersignal.cxp.tui.format_screen import FormatScreen

        self.push_screen(FormatScreen())
