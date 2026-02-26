# Architecture Decision: CounterSignal Monorepo Consolidation

**Status:** Approved
**Date:** 2026-02-25
**Decision:** Single-package monorepo with unified CLI

---

## Context

CounterSignal (formerly Volery) has one released tool (IPI-Canary: v0.1.0, 34 techniques, 7 formats), one scaffolded tool (CXP-Canary: pre-alpha, 3 assistant formats, 13 test files), and one planned tool (RXP: concept doc only). The separate-repo model creates friction: duplicated dev tooling configs, no shared callback infrastructure, and RXP (Phase 2.5) will need to integrate with both existing tools.

The existing `richardspicer/volery` repo is a meta-repo with Roadmap.md, concept docs, and README. It becomes `richardspicer/countersignal` — the home for the consolidated codebase.

**Naming decisions (locked 2026-02-25):**
- **Program:** CounterSignal (PyPI: `countersignal`, claimed)
- **Modules:** IPI (Indirect Prompt Injection), CXP (Context Poisoning), RXP (Retrieval Poisoning)
- **Sister program:** CounterAgent (PyPI: `counteragent`, claimed) handles protocol & system security

## Decision

**Single-package monorepo** — all tools are submodules of one `countersignal` Python package, with a unified CLI entry point (`countersignal ipi`, `countersignal cxp`, `countersignal rxp`). One `pyproject.toml`, one lockfile, one test suite.

**Not chosen:**
- uv workspace packages — adds configuration overhead for a distribution problem that doesn't exist. Rich is the sole developer and always installs the full suite.
- Shared library as a separate repo — inter-repo dependency management pain with no offsetting benefit.
- Status quo (separate repos) — forces RXP into awkward cross-repo imports for callback infrastructure.

## Source Inventory

### IPI-Canary (largest, migrates second)

- **CLI framework:** Typer (already)
- **Models:** Pydantic (Campaign, Hit, HitConfidence, Technique, Format, PayloadStyle, PayloadType)
- **Source files:** ~10 modules + 7 format generators
- **Tests:** 3 test files
- **Key deps:** typer, fastapi, uvicorn, reportlab, rich, pydantic, pypdf, requests, piexif, python-docx, icalendar, jinja2, python-multipart
- **Web dashboard:** FastAPI-based listener with HTMX UI, SQLite DB
- **Entry point:** `ipi-canary = "ipi_canary.cli:app"`

### CXP-Canary (smaller, migrates first)

- **CLI framework:** Click (needs Click→Typer conversion)
- **Models:** dataclasses (Objective, AssistantFormat, Technique, TestResult, Campaign, ValidatorRule, ValidationResult)
- **Source files:** ~10 modules + 3 format modules + 2 objective modules
- **Tests:** 13 test files
- **Key deps:** click, jinja2
- **No web component** — file-based evidence collection
- **Entry point:** `cxp-canary = "cxp_canary.cli:main"`

### RXP (concept only, scaffolded during migration)

- No code exists. Concept doc at `volery/concepts/drongo.md`.
- Will need: embedding model integration, ChromaDB, numpy/scipy for similarity scoring.
- Empty scaffold with `__init__.py` and stub `cli.py` during Phase A.

## Target Structure

```
countersignal/
├── pyproject.toml
├── uv.lock
├── README.md
├── LICENSE
├── AI-STATEMENT.md
├── CLAUDE.md
├── SECURITY.md
├── CONTRIBUTING.md
├── .pre-commit-config.yaml
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── codeql.yml
├── docs/
│   ├── Architecture.md
│   ├── Roadmap.md
│   └── owasp_mapping.md
├── concepts/
│   ├── rxp.md                         # Migrated from volery/concepts/drongo.md
│   └── TEMPLATE.md
├── src/
│   └── countersignal/
│       ├── __init__.py
│       ├── __main__.py                # `python -m countersignal` support
│       ├── cli.py                     # Root Typer app: countersignal [ipi|cxp|rxp]
│       ├── core/
│       │   ├── __init__.py
│       │   ├── models.py             # Campaign, Hit, HitConfidence (callback tracking)
│       │   ├── listener.py           # Callback listener server (extracted from IPI)
│       │   ├── db.py                 # SQLite campaign/hit storage (extracted from IPI)
│       │   └── evidence.py           # Shared evidence collection patterns
│       ├── ipi/
│       │   ├── __init__.py
│       │   ├── cli.py                # IPI subcommands (generate, listen, status, techniques, formats, export)
│       │   ├── models.py             # Format, Technique, PayloadStyle, PayloadType (IPI-specific enums)
│       │   ├── generate_service.py
│       │   ├── generators/
│       │   │   ├── __init__.py
│       │   │   ├── pdf.py
│       │   │   ├── image.py
│       │   │   ├── markdown.py
│       │   │   ├── html.py
│       │   │   ├── docx.py
│       │   │   ├── ics.py
│       │   │   └── eml.py
│       │   ├── server.py             # FastAPI routes (uses core/listener.py)
│       │   ├── api.py
│       │   ├── ui.py
│       │   ├── static/
│       │   │   ├── htmx.min.js
│       │   │   └── style.css
│       │   └── templates/
│       │       ├── layout.html
│       │       ├── dashboard.html
│       │       ├── campaigns.html
│       │       ├── campaign_detail.html
│       │       ├── generate.html
│       │       ├── hits.html
│       │       └── partials/
│       ├── cxp/
│       │   ├── __init__.py
│       │   ├── cli.py                # CXP subcommands (generate, validate, record, report, campaigns)
│       │   ├── models.py             # Objective, AssistantFormat, Technique, TestResult, etc.
│       │   ├── builder.py
│       │   ├── evidence.py
│       │   ├── reporter.py
│       │   ├── validator.py
│       │   ├── formats/
│       │   │   ├── __init__.py
│       │   │   ├── claude_md.py
│       │   │   ├── copilot_instructions.py
│       │   │   └── cursorrules.py
│       │   ├── objectives/
│       │   │   ├── __init__.py
│       │   │   ├── backdoor.py
│       │   │   └── exfil.py
│       │   └── techniques/
│       │       ├── __init__.py
│       │       ├── skeleton/
│       │       └── templates/
│       └── rxp/                       # Phase 2.5 — empty scaffold
│           ├── __init__.py
│           └── cli.py
├── tests/
│   ├── conftest.py                    # Shared fixtures
│   ├── ipi/                           # Migrated from IPI-Canary/tests
│   │   ├── test_db_init.py
│   │   ├── test_path_traversal.py
│   │   └── test_server_defaults.py
│   ├── cxp/                           # Migrated from CXP-Canary/tests
│   │   ├── test_builder.py
│   │   ├── test_cli_campaigns.py
│   │   ├── test_cli_generate.py
│   │   ├── test_cli_record.py
│   │   ├── test_cli_report.py
│   │   ├── test_cli_validate.py
│   │   ├── test_evidence.py
│   │   ├── test_formats.py
│   │   ├── test_models.py
│   │   ├── test_objectives.py
│   │   ├── test_reporter.py
│   │   ├── test_techniques.py
│   │   └── test_validator.py
│   └── core/
│       └── test_listener.py
└── harness/                           # Migrated from IPI-Canary
    └── ...
```

## Shared Code Extraction: What Moves to `core/`

### From IPI-Canary

| Current location | Target | What changes |
|---|---|---|
| `models.py` → `Campaign`, `Hit`, `HitConfidence` | `core/models.py` | Become canonical callback models. IPI-specific enums (Format, Technique, PayloadStyle, PayloadType) stay in `ipi/models.py`. |
| `db.py` | `core/db.py` | Campaign/hit storage is reusable. RXP will track retrieval test campaigns the same way. |
| `server.py` → listener logic | `core/listener.py` | The HTTP callback receiver is shared infrastructure. IPI's `server.py` keeps FastAPI routes/UI but delegates to core listener. |

### From CXP-Canary

Nothing moves to core initially. CXP's `Campaign` dataclass is structurally different from IPI's Pydantic `Campaign` model. Forcing alignment now would be premature.

**Future extraction (post-RXP):** If RXP's campaign tracking looks like IPI's pattern, standardize all three on the core Campaign model. If CXP's pattern diverges permanently, that's fine — tool-specific models are acceptable.

### Core boundary rule

> If RXP will need it from both IPI and CXP → it goes in core.
> If only one tool uses it → it stays in that tool's module.
> When in doubt, keep it tool-specific. Extract later when a second consumer appears.

## CLI Unification

### Framework: Typer

IPI-Canary already uses Typer. CXP-Canary uses Click. Standardize on **Typer** for the unified CLI. Typer is built on Click, so the conversion is straightforward.

### Root CLI

```python
# src/countersignal/cli.py
import typer

app = typer.Typer(
    name="countersignal",
    help="Agentic AI Content & Supply Chain Attack Toolkit",
    no_args_is_help=True,
)

from countersignal.ipi.cli import app as ipi_app
from countersignal.cxp.cli import app as cxp_app

app.add_typer(ipi_app, name="ipi", help="Indirect prompt injection via document ingestion")
app.add_typer(cxp_app, name="cxp", help="Coding assistant context file poisoning")
# Future:
# app.add_typer(rxp_app, name="rxp", help="RAG retrieval poisoning optimizer")
```

### Command mapping

| Old command | New command |
|---|---|
| `ipi-canary generate --callback http://... --technique all` | `countersignal ipi generate --callback http://... --technique all` |
| `ipi-canary listen --port 8080` | `countersignal ipi listen --port 8080` |
| `ipi-canary status` | `countersignal ipi status` |
| `ipi-canary techniques` | `countersignal ipi techniques` |
| `ipi-canary formats` | `countersignal ipi formats` |
| `ipi-canary export` | `countersignal ipi export` |
| `cxp-canary generate ...` | `countersignal cxp generate ...` |
| `cxp-canary validate ...` | `countersignal cxp validate ...` |
| `cxp-canary record ...` | `countersignal cxp record ...` |
| `cxp-canary report ...` | `countersignal cxp report ...` |

**Note:** IPI subcommands keep their names (no `run` rename needed — `generate` is already specific). CXP subcommands keep their names too.

### Entry points

```toml
[project.scripts]
countersignal = "countersignal.cli:app"
```

`ipi-canary` and `cxp-canary` entry points are removed. Old repos archived with full history.

## pyproject.toml

> **Version policy:** Dependency floors reference `[CURRENT STABLE]` — the latest stable PyPI release at implementation time. Claude Code must verify versions via `pip index versions <package>` or PyPI before writing the final `pyproject.toml`.

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "countersignal"
version = "0.1.0"
description = "Agentic AI content & supply chain attack toolkit — indirect prompt injection, context poisoning, and retrieval poisoning"
readme = "README.md"
license = "MIT"
requires-python = ">=3.11"
authors = [
    { name = "Richard Spicer", email = "richard@richardspicer.io" },
]
keywords = ["security", "ai-security", "prompt-injection", "red-team", "rag-poisoning", "context-poisoning"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Intended Audience :: Information Technology",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: Security",
    "Topic :: Software Development :: Testing",
    "Typing :: Typed",
]
dependencies = [
    # CLI & display
    "typer>=[CURRENT STABLE]",
    "rich>=[CURRENT STABLE]",
    # Web listener (IPI dashboard + shared callback server)
    "fastapi>=[CURRENT STABLE]",
    "uvicorn>=[CURRENT STABLE]",
    "python-multipart>=[CURRENT STABLE]",
    "jinja2>=[CURRENT STABLE]",
    # Models & validation
    "pydantic>=[CURRENT STABLE]",
    "requests>=[CURRENT STABLE]",
    # IPI document generators
    "reportlab>=[CURRENT STABLE]",
    "pypdf>=[CURRENT STABLE]",
    "piexif>=[CURRENT STABLE]",
    "python-docx>=[CURRENT STABLE]",
    "icalendar>=[CURRENT STABLE]",
]

[dependency-groups]
dev = [
    "pytest>=[CURRENT STABLE]",
    "pytest-cov>=[CURRENT STABLE]",
    "ruff>=[CURRENT STABLE]",
    "pre-commit>=[CURRENT STABLE]",
    "mypy>=[CURRENT STABLE]",
]

[project.scripts]
countersignal = "countersignal.cli:app"

[project.urls]
Homepage = "https://richardspicer.io"
Repository = "https://github.com/richardspicer/countersignal"
Issues = "https://github.com/richardspicer/countersignal/issues"
Documentation = "https://github.com/richardspicer/countersignal/tree/main/docs"

[tool.hatch.build.targets.wheel]
packages = ["src/countersignal"]
```

Dev tooling configs (ruff, mypy, pytest) are identical across IPI and CXP — merge and deduplicate. Use IPI-Canary's config as the baseline (it has more per-file-ignores for harness/).

### Dependency notes

1. **IPI-heavy deps** (reportlab, piexif, python-docx, icalendar, pypdf) are top-level because IPI is the anchor tool and always installed. If package size becomes a concern later, these could move to `[project.optional-dependencies] ipi = [...]` but that adds install friction for no current benefit.
2. **CXP has minimal deps** — only jinja2 (already in IPI's deps) and click (removed, replaced by typer).
3. **RXP deps** (chromadb, sentence-transformers, numpy) will be added when RXP development begins. Consider optional group at that point if they're heavy.

## Import Rewriting

Every `from ipi_canary.X import Y` and `from cxp_canary.X import Y` changes to `from countersignal.X import Y`.

**Scale:** ~16 test files, ~20 source files across both repos. Smaller than CounterAgent migration.

**Pattern:**

| Old | New |
|---|---|
| `from ipi_canary.models import Campaign, Hit` | `from countersignal.core.models import Campaign, Hit` |
| `from ipi_canary.models import Technique, Format` | `from countersignal.ipi.models import Technique, Format` |
| `from ipi_canary.cli import app` | `from countersignal.ipi.cli import app` |
| `from ipi_canary.db import ...` | `from countersignal.core.db import ...` |
| `from ipi_canary.generate_service import ...` | `from countersignal.ipi.generate_service import ...` |
| `from ipi_canary.generators.pdf import ...` | `from countersignal.ipi.generators.pdf import ...` |
| `from cxp_canary.models import Technique` | `from countersignal.cxp.models import Technique` |
| `from cxp_canary.builder import ...` | `from countersignal.cxp.builder import ...` |
| `from cxp_canary.validator import ...` | `from countersignal.cxp.validator import ...` |

**Approach:** Automated find-and-replace pass, then fix edge cases. Run ruff + mypy + full test suite after.

## Migration Sequence

### Phase A: Scaffold (1 task brief)

1. Rename `richardspicer/volery` repo to `richardspicer/countersignal` on GitHub
2. Create `src/countersignal/` package structure
3. Create `core/__init__.py`, `core/models.py`, `core/listener.py`, `core/db.py`, `core/evidence.py`
4. Create root `cli.py` with Typer app and subcommand mounting stubs
5. Create `__main__.py`
6. Create unified `pyproject.toml` (verify all dep versions)
7. Create empty `ipi/`, `cxp/`, `rxp/` submodules with `__init__.py` and stub `cli.py`
8. Set up `.pre-commit-config.yaml`, ruff, mypy, pytest config
9. Create CLAUDE.md, SECURITY.md, CONTRIBUTING.md, AI-STATEMENT.md
10. **Acceptance:** `uv sync --group dev` succeeds, `countersignal --help` shows subcommands, `pytest` finds 0 tests

### Phase B: Migrate CXP (1 task brief)

CXP migrates first because it's smaller, has no web component, and validates the architecture without risking the anchor tool.

1. Copy CXP-Canary source into `src/countersignal/cxp/`
2. Convert CLI from Click to Typer
3. Rewrite imports across all CXP source files
4. Copy tests into `tests/cxp/`, rewrite imports
5. **Acceptance:** `countersignal cxp --help` works, all CXP tests pass, ruff + mypy clean

### Phase C: Migrate IPI (1-2 task briefs)

IPI is larger and has the web dashboard, so it migrates after CXP proves the structure.

1. Extract Campaign, Hit, HitConfidence from `ipi_canary/models.py` into `core/models.py`
2. Extract `ipi_canary/db.py` into `core/db.py`
3. Extract listener logic from `ipi_canary/server.py` into `core/listener.py`
4. Copy remaining IPI-Canary source into `src/countersignal/ipi/`
5. IPI-specific enums (Format, Technique, PayloadStyle, PayloadType) stay in `ipi/models.py`
6. Wire `ipi/cli.py` as Typer subcommand group (already Typer — minimal changes)
7. Rewrite imports across all IPI source files
8. Copy tests into `tests/ipi/`, rewrite imports
9. Copy harness/ into repo root
10. Verify static file and template paths resolve from new location
11. **Acceptance:** `countersignal ipi generate --help` works, `countersignal ipi listen` starts, all IPI tests pass, ruff + mypy clean

### Phase D: Integration & cleanup (1 task brief)

1. Run full unified test suite — all 16+ tests pass
2. Verify `countersignal ipi generate --callback http://... --technique all` produces correct documents
3. Verify `countersignal ipi listen` serves dashboard and receives callbacks
4. Update `docs/Architecture.md` to reflect unified structure
5. Update `Roadmap.md` with monorepo status
6. Update `README.md` with new install/usage instructions
7. Update `CLAUDE.md` for unified repo context
8. Set up unified CI (`.github/workflows/ci.yml`) — test matrix: ubuntu-latest + windows-latest
9. **Acceptance:** Full CI green, both `countersignal ipi` and `countersignal cxp` work end-to-end

### Phase E: Deprecate old repos

1. Update `richardspicer/IPI-Canary` README: deprecation notice → countersignal
2. Update `richardspicer/CXP-Canary` README: deprecation notice → countersignal
3. Archive both repos on GitHub (read-only)
4. Update Obsidian Handoff, Kanban, and Project Instructions

## Git History

**Approach:** Copy files, don't preserve per-file git history.

Rationale: Import rewriting means every file changes. The old repos stay archived with full history. The countersignal repo starts fresh with clear "Migration: CXP-Canary" and "Migration: IPI-Canary" commits.

## CXP Click→Typer Conversion Notes

CXP-Canary uses Click with `@click.group()` / `@click.command()` decorators. The conversion is mechanical:

| Click pattern | Typer equivalent |
|---|---|
| `@click.group()` | `app = typer.Typer()` |
| `@click.command()` | `@app.command()` |
| `@click.option('--name', type=str)` | `name: Annotated[str, typer.Option()]` |
| `@click.argument('path')` | `path: Annotated[Path, typer.Argument()]` |
| `click.echo()` | `typer.echo()` or Rich console |

CXP has 5 CLI commands across test files. The conversion is Phase B scope — straightforward given the small surface area.

## CXP Dataclass→Pydantic Decision

**Decision: Keep dataclasses for now.** CXP uses plain dataclasses, IPI uses Pydantic. Forcing CXP onto Pydantic during migration adds unnecessary risk. The models are internal — they don't cross module boundaries. If CXP later needs validation/serialization features, convert then.

## Risk Checklist

- [ ] Typer `add_typer()` works for nested subcommand groups — verified in CounterAgent migration
- [ ] `hatchling` discovers `src/countersignal` with nested submodules correctly
- [ ] FastAPI static file and Jinja2 template paths resolve from `ipi/static/` and `ipi/templates/`
- [ ] SQLite DB path resolution works from new package location
- [ ] CXP Jinja2 technique templates resolve from `cxp/techniques/templates/`
- [ ] CXP skeleton files resolve from `cxp/techniques/skeleton/`
- [ ] GitHub Push Protection doesn't block IPI harness files
- [ ] CLAUDE.md guardrails carry forward
- [ ] Pre-commit hooks work with unified config
- [ ] `countersignal` name doesn't conflict with any stdlib or common package

## Go/No-Go Checkpoint

After Phase B (CXP migration complete), run the full CXP test suite and verify `countersignal cxp generate` produces correct output. If this works, the architecture is proven and Phase C (IPI) proceeds. If structural issues emerge, reassess before migrating the anchor tool.

## Not In Scope

- PyPI publishing of real release (placeholder `0.0.1.dev0` already claimed)
- Docker image
- RXP implementation (empty scaffold only)
- Shared `--callback-url` flag across modules (future, when RXP needs callbacks)
- Migrating IPI's web dashboard to a shared service (future, if CXP/RXP need dashboards)
- Detection engineering / Sigma rules (separate track)
