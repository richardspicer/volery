"""IPI subcommands — indirect prompt injection via document ingestion."""

import typer

app = typer.Typer(no_args_is_help=True)


@app.command()
def placeholder() -> None:
    """Placeholder — IPI commands will be available after migration."""
    typer.echo("IPI module not yet migrated. See Phase C of the migration plan.")
