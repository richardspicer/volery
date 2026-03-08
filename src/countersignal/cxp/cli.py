"""CXP subcommands — coding assistant context file poisoning."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Annotated, NoReturn

import typer

from countersignal.cxp.evidence import (
    create_campaign,
    get_campaign,
    get_db,
    get_result,
    list_campaigns,
    list_results,
    record_result,
    update_validation,
)
from countersignal.cxp.formats import list_formats
from countersignal.cxp.objectives import list_objectives
from countersignal.cxp.techniques import get_technique, list_techniques
from countersignal.cxp.validator import validate as run_validation

app = typer.Typer(no_args_is_help=True)

report_app = typer.Typer(no_args_is_help=True)
app.add_typer(report_app, name="report", help="Generate comparison matrices and PoC packages.")


def _error(message: str) -> NoReturn:
    """Print error and exit."""
    typer.echo(f"Error: {message}", err=True)
    raise typer.Exit(code=1)


@app.command()
def objectives() -> None:
    """List available attack objectives."""
    objs = list_objectives()
    if not objs:
        typer.echo("No objectives registered.")
        return
    typer.echo(f"{'ID':<20} {'Name':<30} Description")
    typer.echo("-" * 80)
    for obj in objs:
        typer.echo(f"{obj.id:<20} {obj.name:<30} {obj.description}")


@app.command()
def formats() -> None:
    """List supported assistant formats."""
    fmts = list_formats()
    if not fmts:
        typer.echo("No formats registered.")
        return
    typer.echo(f"{'ID':<25} {'Filename':<35} {'Assistant':<20} Syntax")
    typer.echo("-" * 95)
    for fmt in fmts:
        typer.echo(f"{fmt.id:<25} {fmt.filename:<35} {fmt.assistant:<20} {fmt.syntax}")


@app.command()
def techniques() -> None:
    """List all techniques (objective x format matrix)."""
    techs = list_techniques()
    if not techs:
        typer.echo("No techniques registered.")
        return
    typer.echo(f"{'Technique ID':<35} {'Objective':<20} {'Format':<25} Type")
    typer.echo("-" * 95)
    for tech in techs:
        typer.echo(
            f"{tech.id:<35} {tech.objective.id:<20} {tech.format.id:<25} {tech.project_type}"
        )


@app.command()
def record(
    technique: Annotated[str, typer.Option(help="Technique ID to test.")],
    assistant: Annotated[str, typer.Option(help="Assistant under test.")],
    trigger_prompt: Annotated[str, typer.Option(help="Prompt used to trigger.")],
    files: Annotated[
        list[Path] | None, typer.Option("--file", help="Path to assistant-generated code file(s).")
    ] = None,
    output_file: Annotated[
        Path | None,
        typer.Option(help="Path to saved chat output file.", exists=True),
    ] = None,
    campaign_id: Annotated[
        str | None, typer.Option("--campaign", help="Existing campaign ID.")
    ] = None,
    model: Annotated[str, typer.Option(help="Underlying model name.")] = "",
    notes: Annotated[str, typer.Option(help="Researcher observations.")] = "",
    db_path: Annotated[
        Path | None, typer.Option("--db", help="Database path (default: ~/.countersignal/cxp.db).")
    ] = None,
) -> None:
    """Record a test result into the evidence store."""
    file_list = files or []

    # Validate mutual exclusivity
    if file_list and output_file:
        _error("--file and --output-file are mutually exclusive.")
    if not file_list and not output_file:
        _error("Either --file or --output-file is required.")

    # Validate file existence for --file (Typer doesn't validate list[Path] existence)
    for f in file_list:
        if not f.exists():
            _error(f"Invalid value for '--file': Path '{f}' does not exist.")

    # Validate technique
    if get_technique(technique) is None:
        _error(f"Unknown technique: {technique}")

    # Determine capture mode and raw output
    captured_files: list[str] = []
    if file_list:
        capture_mode = "file"
        captured_files = [str(f) for f in file_list]
        raw_output = "\n".join(f.read_text(encoding="utf-8", errors="replace") for f in file_list)
    else:
        capture_mode = "output"
        if output_file is None:
            raise typer.BadParameter("--output-file is required for output capture mode")
        raw_output = output_file.read_text(encoding="utf-8", errors="replace")

    # Open DB and resolve campaign
    conn = get_db(db_path)
    if campaign_id:
        campaign = get_campaign(conn, campaign_id)
        if campaign is None:
            conn.close()
            _error(f"Campaign not found: {campaign_id}")
    else:
        name = f"{date.today().isoformat()}-{assistant}"
        campaign = create_campaign(conn, name)

    result = record_result(
        conn,
        campaign_id=campaign.id,
        technique_id=technique,
        assistant=assistant,
        trigger_prompt=trigger_prompt,
        raw_output=raw_output,
        capture_mode=capture_mode,
        model=model,
        captured_files=captured_files,
        notes=notes,
    )
    conn.close()

    typer.echo(f"Result:   {result.id}")
    typer.echo(f"Campaign: {campaign.id}")


@app.command()
def campaigns(
    campaign_id: Annotated[str | None, typer.Argument()] = None,
    db_path: Annotated[
        Path | None, typer.Option("--db", help="Database path (default: ~/.countersignal/cxp.db).")
    ] = None,
) -> None:
    """List campaigns and results."""
    conn = get_db(db_path)

    if campaign_id is None:
        # List all campaigns
        camps = list_campaigns(conn)
        if not camps:
            typer.echo("No campaigns found.")
            conn.close()
            return
        typer.echo(f"{'ID':<38} {'Name':<30} {'Created':<22} Results")
        typer.echo("-" * 95)
        for c in camps:
            count = len(list_results(conn, c.id))
            created_str = c.created.strftime("%Y-%m-%d %H:%M")
            typer.echo(f"{c.id:<38} {c.name:<30} {created_str:<22} {count}")
    else:
        # Show campaign detail
        campaign = get_campaign(conn, campaign_id)
        if campaign is None:
            conn.close()
            _error(f"Campaign not found: {campaign_id}")
        typer.echo(f"Campaign: {campaign.name}")
        typer.echo(f"ID:       {campaign.id}")
        typer.echo(f"Created:  {campaign.created.isoformat()}")
        if campaign.description:
            typer.echo(f"Desc:     {campaign.description}")
        results = list_results(conn, campaign.id)
        typer.echo(f"\nResults ({len(results)}):")
        if results:
            typer.echo(f"  {'ID':<38} {'Technique':<30} {'Assistant':<20} Status")
            typer.echo("  " + "-" * 93)
            for r in results:
                typer.echo(
                    f"  {r.id:<38} {r.technique_id:<30} {r.assistant:<20} {r.validation_result}"
                )
    conn.close()


@app.command()
def generate(
    objective: Annotated[str | None, typer.Option(help="Filter by objective ID.")] = None,
    format_id: Annotated[str | None, typer.Option("--format", help="Filter by format ID.")] = None,
    output_dir: Annotated[Path, typer.Option(help="Output directory (default: ./repos).")] = Path(
        "./repos"
    ),
    research: Annotated[
        bool,
        typer.Option(
            "--research",
            help="Include security warnings and TRIGGER.md (for documentation, not testing).",
        ),
    ] = False,
) -> None:
    """Generate poisoned test repositories."""
    from countersignal.cxp.builder import build_all

    repos = build_all(output_dir, objective=objective, format_id=format_id, research=research)
    for repo in repos:
        typer.echo(f"  {repo.name}")
    if research:
        typer.echo(
            f"Generated {len(repos)} research repo(s) in {output_dir}"
            " (with security warnings and TRIGGER.md)"
        )
    else:
        typer.echo(
            f"Generated {len(repos)} clean test repo(s) in {output_dir}."
            f" Testing instructions: {output_dir / 'manifest.json'}"
        )


@app.command()
def validate(
    result_id: Annotated[
        str | None, typer.Option("--result", help="Stored result ID to validate.")
    ] = None,
    technique: Annotated[
        str | None, typer.Option(help="Technique ID (for file validation).")
    ] = None,
    files: Annotated[
        list[Path] | None, typer.Option("--file", help="Path to file(s) to validate.")
    ] = None,
    db_path: Annotated[
        Path | None, typer.Option("--db", help="Database path (default: ~/.countersignal/cxp.db).")
    ] = None,
) -> None:
    """Validate captured output against detection rules."""
    file_list = files or []

    if result_id is None and technique is None:
        _error("Either --result or --technique is required.")

    if result_id is not None:
        # Mode A: Validate stored result
        conn = get_db(db_path)
        try:
            stored = get_result(conn, result_id)
            if stored is None:
                _error(f"Result not found: {result_id}")
            vr = run_validation(stored.raw_output, stored.technique_id)
            update_validation(conn, result_id, vr.verdict, vr.details)
        finally:
            conn.close()
    else:
        # Mode B: Validate file(s) directly
        if technique is None:
            _error("--technique is required.")
        if not file_list:
            _error("--file is required when using --technique.")
        # Validate file existence
        for f in file_list:
            if not f.exists():
                _error(f"Invalid value for '--file': Path '{f}' does not exist.")
        if get_technique(technique) is None:
            _error(f"Unknown technique: {technique}")
        raw_output = "\n".join(f.read_text(encoding="utf-8", errors="replace") for f in file_list)
        vr = run_validation(raw_output, technique)

    typer.echo(f"Verdict: {vr.verdict}")
    if vr.matched_rules:
        typer.echo(f"Matched: {', '.join(vr.matched_rules)}")
    typer.echo(f"Details: {vr.details}")


@report_app.command()
def matrix(
    campaign_id: Annotated[
        str | None, typer.Option("--campaign", help="Filter to specific campaign.")
    ] = None,
    output_format: Annotated[
        str, typer.Option("--format", help="Output format (default: markdown).")
    ] = "markdown",
    output_path: Annotated[
        Path | None, typer.Option("--output", help="Write to file instead of stdout.")
    ] = None,
    db_path: Annotated[
        Path | None, typer.Option("--db", help="Database path (default: ~/.countersignal/cxp.db).")
    ] = None,
) -> None:
    """Generate an assistant comparison matrix."""
    if output_format not in ("markdown", "json"):
        _error(f"Invalid format: {output_format}. Choose 'markdown' or 'json'.")

    from countersignal.cxp.reporter import generate_matrix, matrix_to_json, matrix_to_markdown

    conn = get_db(db_path)
    try:
        data = generate_matrix(conn, campaign_id=campaign_id)
    finally:
        conn.close()

    content = matrix_to_json(data) if output_format == "json" else matrix_to_markdown(data)

    if output_path:
        output_path.write_text(content, encoding="utf-8")
        typer.echo(f"Report written to {output_path}")
    else:
        typer.echo(content)


@report_app.command()
def poc(
    result_id: Annotated[str, typer.Option("--result", help="Test result ID to package.")],
    output_path: Annotated[
        Path | None,
        typer.Option("--output", help="Output zip path (default: ./poc-{technique}.zip)."),
    ] = None,
    db_path: Annotated[
        Path | None, typer.Option("--db", help="Database path (default: ~/.countersignal/cxp.db).")
    ] = None,
) -> None:
    """Export a bounty-ready PoC package."""
    from countersignal.cxp.reporter import export_poc

    conn = get_db(db_path)
    try:
        # Determine default output path from the result's technique
        if output_path is None:
            stored = get_result(conn, result_id)
            if stored is None:
                _error(f"Result not found: {result_id}")
            output_path = Path(f"poc-{stored.technique_id}.zip")

        created = export_poc(conn, result_id, output_path)
        typer.echo(f"PoC package: {created}")
    except ValueError as e:
        _error(str(e))
    finally:
        conn.close()
