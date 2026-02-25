"""CXP subcommands — coding assistant context file poisoning."""

import typer

app = typer.Typer(no_args_is_help=True)


@app.command()
def placeholder() -> None:
    """Placeholder — CXP commands will be available after migration."""
    typer.echo("CXP module not yet migrated. See Phase B of the migration plan.")
