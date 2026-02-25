"""CounterSignal CLI — Agentic AI content & supply chain attack toolkit."""

import typer

from countersignal.cxp.cli import app as cxp_app
from countersignal.ipi.cli import app as ipi_app
from countersignal.rxp.cli import app as rxp_app

app = typer.Typer(
    name="countersignal",
    help="Agentic AI content & supply chain attack toolkit.\n\n"
    "Indirect prompt injection (ipi), context poisoning (cxp), "
    "and retrieval poisoning (rxp).",
    no_args_is_help=True,
)

app.add_typer(ipi_app, name="ipi", help="Indirect prompt injection via document ingestion")
app.add_typer(cxp_app, name="cxp", help="Coding assistant context file poisoning")
app.add_typer(rxp_app, name="rxp", help="RAG retrieval poisoning optimizer [planned]")
