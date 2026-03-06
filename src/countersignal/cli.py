"""CounterSignal CLI — Agentic AI content & supply chain attack toolkit."""

import typer

from countersignal.cxp.cli import app as cxp_app
from countersignal.ipi.cli import app as ipi_app
from countersignal.rxp.cli import app as rxp_app


def _parse_version(v: str) -> tuple[int, ...]:
    """Parse a semver-like version string into a comparable tuple.

    Args:
        v: Version string (e.g. "0.1.0").

    Returns:
        Tuple of integers (e.g. (0, 1, 0)).
    """
    try:
        return tuple(int(x) for x in v.split("."))
    except ValueError:
        return (0,)


def _check_for_update(package_name: str) -> None:
    """Non-blocking background PyPI version check.

    Spawns a daemon thread that fetches the latest version from PyPI
    and prints a one-liner to stderr if a newer version is available.
    Silent on any network or parse failure.

    Args:
        package_name: PyPI package name (e.g. "countersignal").
    """
    import json
    import sys
    import threading
    from importlib.metadata import version
    from urllib.request import urlopen

    def _check() -> None:
        try:
            current = version(package_name)
            url = f"https://pypi.org/pypi/{package_name}/json"
            with urlopen(url, timeout=3) as resp:  # noqa: S310
                data = json.loads(resp.read())
            latest = data["info"]["version"]
            if _parse_version(latest) > _parse_version(current):
                print(
                    f"Update available: {package_name} {current} \u2192 {latest}  "
                    f"(pip install --upgrade {package_name})",
                    file=sys.stderr,
                )
        except Exception:  # noqa: BLE001, S110
            pass

    threading.Thread(target=_check, daemon=True).start()


app = typer.Typer(
    name="countersignal",
    help="Agentic AI content & supply chain attack toolkit.\n\n"
    "Indirect prompt injection (ipi), context poisoning (cxp), "
    "and retrieval poisoning (rxp).",
)


@app.callback(invoke_without_command=True)
def _on_startup(ctx: typer.Context) -> None:
    """Run pre-invocation hooks."""
    _check_for_update("countersignal")
    if ctx.invoked_subcommand is None:
        import click

        click.echo(ctx.get_help())
        raise typer.Exit()


app.add_typer(ipi_app, name="ipi", help="Indirect prompt injection via document ingestion")
app.add_typer(cxp_app, name="cxp", help="Coding assistant context file poisoning")
app.add_typer(rxp_app, name="rxp", help="RAG retrieval poisoning optimizer")
