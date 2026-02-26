# CounterSignal Monorepo Scaffold — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create the empty monorepo skeleton for CounterSignal — package structure, dev tooling, CI, standard docs — with no migrated code.

**Architecture:** Python monorepo under `src/countersignal/` using hatchling build, Typer CLI with `ipi`, `cxp`, `rxp` subcommand stubs, uv package manager with PEP 735 dependency groups. Mirrors `counteragent` project layout and conventions.

**Tech Stack:** Python >=3.11, Typer, hatchling, uv, ruff, mypy, pytest, pre-commit, GitHub Actions

**Reference repo:** `C:\Users\richs\code\richardspicer\counteragent` — follow its patterns for project layout, CI, dev tooling, and standard docs.

---

## Task 1: Create Feature Branch + .gitignore

**Files:**
- Create: `.gitignore`

**Step 1: Create feature branch**

```bash
cd C:\Users\richs\code\richardspicer\countersignal
git checkout -b feature/scaffold-monorepo
```

**Step 2: Write .gitignore**

Create `.gitignore` with Python standard ignores plus project-specific entries:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so

# Distribution / packaging
dist/
build/
*.egg-info/
*.egg

# Virtual environments
.venv/
venv/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Testing
.pytest_cache/
.coverage
htmlcov/

# mypy
.mypy_cache/

# ruff
.ruff_cache/

# OS
.DS_Store
Thumbs.db

# Project
*.db
.commitmsg
scripts/preflight.py

.claude/settings.local.json
```

**Step 3: Commit**

```bash
git add .gitignore
git commit -m "chore: add Python .gitignore"
```

---

## Task 2: Clean Existing Content

**Files:**
- Rename: `concepts/drongo.md` → `concepts/rxp.md`
- Move: `Roadmap.md` → `docs/Roadmap.md`
- Modify: `AI-STATEMENT.md` (no Volery refs to fix — already clean)
- Modify: `concepts/rxp.md` (update title + Volery refs)
- Modify: `concepts/TEMPLATE.md` (update Volery ref)
- Delete: `README.md` (will be rewritten in Task 12)

**Step 1: Rename drongo.md → rxp.md and update content**

```bash
git mv concepts/drongo.md concepts/rxp.md
```

Edit `concepts/rxp.md`:
- Line 1: Change `# Drongo` → `# RXP`
- Line 11: Change `Phase 2.5 in the Volery program.` → `Phase 2.5 in the CounterSignal program.`
- Line 17: Update note about standalone vs module — the ADR decided on monorepo module, so update: `"May be implemented as a standalone repo..."` → `"Implemented as the rxp module within the countersignal monorepo."`

**Step 2: Update TEMPLATE.md**

Edit `concepts/TEMPLATE.md` line 11: Change `Volery program` → `CounterSignal program`.

**Step 3: Move Roadmap.md to docs/**

```bash
git mv Roadmap.md docs/Roadmap.md
```

Edit `docs/Roadmap.md` line 7: Change `Volery is the` → `CounterSignal is the`.

**Step 4: Delete old README.md** (will be rewritten in Task 12)

```bash
git rm README.md
```

**Step 5: Commit**

```bash
git add -A
git commit -m "chore: reorganize existing content for monorepo scaffold

Rename concepts/drongo.md to concepts/rxp.md, move Roadmap to docs/,
update Volery references to CounterSignal."
```

---

## Task 3: Package Directory Structure

**Files:**
- Create: `src/countersignal/__init__.py`
- Create: `src/countersignal/__main__.py`
- Create: `src/countersignal/core/__init__.py`
- Create: `src/countersignal/core/models.py`
- Create: `src/countersignal/core/listener.py`
- Create: `src/countersignal/core/db.py`
- Create: `src/countersignal/core/evidence.py`
- Create: `src/countersignal/ipi/__init__.py`
- Create: `src/countersignal/cxp/__init__.py`
- Create: `src/countersignal/rxp/__init__.py`

Every `__init__.py` has a module-level docstring. Empty modules have a docstring only.

**Step 1: Create all package directories and __init__.py files**

`src/countersignal/__init__.py`:
```python
"""CounterSignal — Agentic AI content & supply chain attack toolkit."""

__version__ = "0.1.0"
```

`src/countersignal/__main__.py`:
```python
"""python -m countersignal support."""

from countersignal.cli import app

app()
```

`src/countersignal/core/__init__.py`:
```python
"""Shared infrastructure: callback tracking, storage, evidence."""
```

`src/countersignal/core/models.py`:
```python
"""Shared data models for callback tracking."""
```

`src/countersignal/core/listener.py`:
```python
"""Callback listener server."""
```

`src/countersignal/core/db.py`:
```python
"""Campaign and hit storage."""
```

`src/countersignal/core/evidence.py`:
```python
"""Shared evidence collection patterns."""
```

`src/countersignal/ipi/__init__.py`:
```python
"""IPI — Indirect prompt injection via document ingestion."""
```

`src/countersignal/cxp/__init__.py`:
```python
"""CXP — Coding assistant context file poisoning."""
```

`src/countersignal/rxp/__init__.py`:
```python
"""RXP — RAG retrieval poisoning optimizer."""
```

**Step 2: Verify directory structure**

```bash
find src/ -type f -name "*.py" | sort
```

Expected output:
```
src/countersignal/__init__.py
src/countersignal/__main__.py
src/countersignal/core/__init__.py
src/countersignal/core/db.py
src/countersignal/core/evidence.py
src/countersignal/core/listener.py
src/countersignal/core/models.py
src/countersignal/cxp/__init__.py
src/countersignal/ipi/__init__.py
src/countersignal/rxp/__init__.py
```

**Note:** Do NOT commit yet — Task 4 adds CLI files that are imported by `__main__.py`. Committing now would leave a broken import.

---

## Task 4: CLI Code

**Files:**
- Create: `src/countersignal/cli.py`
- Create: `src/countersignal/ipi/cli.py`
- Create: `src/countersignal/cxp/cli.py`
- Create: `src/countersignal/rxp/cli.py`

**Step 1: Write subcommand stubs first** (root CLI imports these)

`src/countersignal/ipi/cli.py`:
```python
"""IPI subcommands — indirect prompt injection via document ingestion."""

import typer

app = typer.Typer(no_args_is_help=True)


@app.command()
def placeholder() -> None:
    """Placeholder — IPI commands will be available after migration."""
    typer.echo("IPI module not yet migrated. See Phase C of the migration plan.")
```

`src/countersignal/cxp/cli.py`:
```python
"""CXP subcommands — coding assistant context file poisoning."""

import typer

app = typer.Typer(no_args_is_help=True)


@app.command()
def placeholder() -> None:
    """Placeholder — CXP commands will be available after migration."""
    typer.echo("CXP module not yet migrated. See Phase B of the migration plan.")
```

`src/countersignal/rxp/cli.py`:
```python
"""RXP subcommands — RAG retrieval poisoning optimizer."""

import typer

app = typer.Typer(no_args_is_help=True)


@app.command()
def placeholder() -> None:
    """Placeholder — RXP commands will be available when planned."""
    typer.echo("RXP module not yet implemented. See the project roadmap.")
```

**Step 2: Write root CLI**

`src/countersignal/cli.py`:
```python
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
```

**Note:** Imports are at the top (not inline after `app` declaration) to satisfy ruff import ordering rules (E402). The task brief showed inline imports, but ruff will flag them.

**Step 3: Commit package structure + CLI together**

```bash
git add src/
git commit -m "feat: add package structure with Typer CLI stubs

Root CLI mounts ipi, cxp, rxp subcommands. All stubs have placeholder
commands. Core module has empty model/listener/db/evidence files."
```

---

## Task 5: pyproject.toml

**Files:**
- Create: `pyproject.toml`

**Step 1: Verify dependency versions** (optional — use brief's versions as fallback)

```bash
pip index versions typer 2>/dev/null | head -3
pip index versions rich 2>/dev/null | head -3
pip index versions fastapi 2>/dev/null | head -3
pip index versions pydantic 2>/dev/null | head -3
```

If `pip index versions` is unavailable, use the versions from the task brief — they're verified as of 2026-02-25.

**Step 2: Write pyproject.toml**

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
    "Development Status :: 2 - Pre-Alpha",
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
    "typer>=0.24.0",
    "rich>=13.0.0",
    # Web listener (IPI dashboard + shared callback server)
    "fastapi>=0.133.0",
    "uvicorn>=0.34.0",
    "python-multipart>=0.0.20",
    "jinja2>=3.1.0",
    # Models & validation
    "pydantic>=2.11.0",
    "requests>=2.32.0",
    # IPI document generators
    "reportlab>=4.4.0",
    "pypdf>=5.0.0",
    "piexif>=1.1.3",
    "python-docx>=1.2.0",
    "icalendar>=6.0.0",
]

[dependency-groups]
dev = [
    "pytest>=8.3.0",
    "pytest-cov>=6.0.0",
    "ruff>=0.9.0",
    "pre-commit>=4.3.0",
    "mypy>=1.15.0",
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

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "B", "C90", "UP", "S"]
ignore = ["S101", "S104", "S311"]

[tool.ruff.lint.mccabe]
max-complexity = 15

[tool.ruff.lint.per-file-ignores]
"harness/*" = ["S", "E501", "C901"]
"scripts/*" = ["S", "E501"]
"tests/*" = ["S"]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
check_untyped_defs = true
ignore_missing_imports = true

[[tool.mypy.overrides]]
module = "harness.*"
ignore_errors = true

[[tool.mypy.overrides]]
module = "scripts.*"
ignore_errors = true

[[tool.mypy.overrides]]
module = "tests.*"
ignore_errors = true
```

**Step 3: Commit**

```bash
git add pyproject.toml
git commit -m "feat: add pyproject.toml with merged dependencies

Hatchling build, Typer CLI entry point, merged IPI+CXP deps,
PEP 735 dev group, ruff/mypy/pytest config."
```

---

## Task 6: Install + Verify CLI

**Step 1: Install dependencies**

```bash
uv sync --group dev
```

Expected: succeeds without errors, creates `.venv/` and `uv.lock`.

**Step 2: Verify root CLI**

```bash
uv run countersignal --help
```

Expected: shows help with `ipi`, `cxp`, `rxp` subcommands listed.

**Step 3: Verify subcommands**

```bash
uv run countersignal ipi --help
uv run countersignal cxp --help
uv run countersignal rxp --help
```

Expected: each shows placeholder command help text.

**Step 4: Verify python -m**

```bash
uv run python -m countersignal --help
```

Expected: same output as `countersignal --help`.

**Step 5: Run ruff**

```bash
uv run ruff check .
uv run ruff format --check .
```

Expected: both pass clean. If ruff finds issues, fix them before proceeding.

**Step 6: Run mypy**

```bash
uv run mypy src/countersignal/
```

Expected: passes clean (Success: no issues found).

**No commit** — this is a verification-only task.

---

## Task 7: Tests Directory

**Files:**
- Create: `tests/conftest.py`
- Create: `tests/core/__init__.py`
- Create: `tests/ipi/__init__.py`
- Create: `tests/cxp/__init__.py`

**Step 1: Create test directory structure**

`tests/conftest.py`:
```python
"""Shared test fixtures for CounterSignal."""
```

`tests/core/__init__.py`:
```python
```

`tests/ipi/__init__.py`:
```python
```

`tests/cxp/__init__.py`:
```python
```

(The `__init__.py` files are empty — no docstrings needed for test packages.)

**Step 2: Verify pytest runs**

```bash
uv run pytest -q
```

Expected: exit code 5 (no tests collected). This is acceptable per the task brief.

**Step 3: Commit**

```bash
git add tests/
git commit -m "chore: add empty test directory structure

conftest.py + core/ipi/cxp subdirectories. Tests arrive in Phases B-C."
```

---

## Task 8: Pre-commit Config

**Files:**
- Create: `.pre-commit-config.yaml`

**Step 1: Write pre-commit config**

Use counteragent's config as the base (already has current hook revisions):

```yaml
# Pre-commit hooks for countersignal
# Install: pre-commit install
# Run all: pre-commit run --all-files
# Update: pre-commit autoupdate

repos:
  # General file hygiene
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-merge-conflict
      - id: no-commit-to-branch
        args: ['--branch', 'main']

  # Ruff linter + formatter
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.0
    hooks:
      - id: ruff-check
        args: ['--fix']
      - id: ruff-format

  # Secrets detection
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.30.0
    hooks:
      - id: gitleaks

  # Mypy type checker
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.19.1
    hooks:
      - id: mypy
        args: ['--config-file=pyproject.toml']
        additional_dependencies: ['pydantic>=2.0']
```

**Step 2: Install pre-commit**

```bash
uv run pre-commit install
```

Expected: "pre-commit installed at .git/hooks/pre-commit"

**Step 3: Run pre-commit autoupdate** (get latest hook revisions)

```bash
uv run pre-commit autoupdate
```

Update the `.pre-commit-config.yaml` with whatever revisions autoupdate produces.

**Step 4: Run pre-commit on all files**

```bash
uv run pre-commit run --all-files
```

Expected: all hooks pass. If any fail (e.g., trailing whitespace, end-of-file-fixer), let them auto-fix and re-stage.

**Step 5: Commit**

```bash
git add .pre-commit-config.yaml
git commit -m "chore: add pre-commit config

Hooks: trailing-whitespace, end-of-file-fixer, check-yaml, check-toml,
check-added-large-files, check-merge-conflict, no-commit-to-branch,
ruff-check, ruff-format, gitleaks, mypy."
```

**Watch out:** The `no-commit-to-branch` hook blocks commits to `main`. We're on `feature/scaffold-monorepo`, so this is fine. But if you forgot to create the branch in Task 1, this hook will block you.

---

## Task 9: CI Workflows

**Files:**
- Create: `.github/workflows/ci.yml`
- Create: `.github/workflows/codeql.yml`

**Step 1: Write CI workflow**

`.github/workflows/ci.yml` — copied from counteragent, adapted for countersignal:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint-and-test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
        python-version: ["3.11", "3.13"]

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v5

      - name: Set up Python ${{ matrix.python-version }}
        run: uv python install ${{ matrix.python-version }}

      - name: Install dependencies
        run: uv sync --group dev

      - name: Lint
        run: uv run ruff check .

      - name: Type check
        run: uv run mypy src/

      - name: Test
        # Exit code 5 = no tests collected (expected until Phase B adds tests)
        run: uv run pytest -q || test $? -eq 5
        shell: bash

      - name: Smoke test CLI
        run: uv run countersignal --help
```

**Step 2: Write CodeQL workflow**

`.github/workflows/codeql.yml` — identical to counteragent:

```yaml
name: "CodeQL"

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: "0 12 * * 6"

jobs:
  analyze:
    name: Analyze
    runs-on: ubuntu-latest

    permissions:
      security-events: write
      contents: read

    strategy:
      fail-fast: false
      matrix:
        language: ["python"]

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Initialize CodeQL
        uses: github/codeql-action/init@v4
        with:
          languages: ${{ matrix.language }}
          build-mode: none

      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v4
        with:
          category: "/language:${{ matrix.language }}"
```

**Step 3: Commit**

```bash
git add .github/
git commit -m "ci: add CI and CodeQL workflows

CI: matrix (ubuntu + windows, Python 3.11 + 3.13), ruff, mypy, pytest, CLI smoke test.
CodeQL: weekly schedule + push/PR on main."
```

---

## Task 10: Standard Docs — LICENSE, SECURITY.md, CONTRIBUTING.md

**Files:**
- Create: `LICENSE`
- Create: `SECURITY.md`
- Create: `CONTRIBUTING.md`

**Step 1: Write MIT LICENSE**

```
MIT License

Copyright (c) 2026 Richard Spicer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

**Step 2: Write SECURITY.md** (adapted from counteragent)

```markdown
# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in CounterSignal, please report it responsibly:

1. **Do not** open a public GitHub issue for security vulnerabilities
2. Email **richard@richardspicer.io** with:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact assessment
3. Allow up to 72 hours for initial response
4. We will coordinate disclosure timeline with you

## Scope

CounterSignal is a security testing tool. Vulnerabilities in the tool itself (not in targets being tested) are in scope:

- Command injection in CLI argument handling
- Credential leakage in reports or logs
- Dependency vulnerabilities with exploitable paths
- Unsafe deserialization of scan results or callback data

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |
```

**Step 3: Write CONTRIBUTING.md** (adapted from counteragent, MIT license)

```markdown
# Contributing to CounterSignal

## Development Setup

```bash
git clone https://github.com/richardspicer/countersignal.git
cd countersignal
uv sync --group dev
uv run pre-commit install
```

## Branch Workflow

**Never commit directly to main.** Branch protection is enforced.

```bash
git checkout main && git pull
git checkout -b feature/your-description
# ... work ...
git push -u origin feature/your-description
```

## Before Committing

1. **Tests pass:** `uv run pytest -q`
2. **Lint clean:** `uv run ruff check .`
3. **Types clean:** `uv run mypy src/`
4. **CLI works:** `uv run countersignal --help`

Pre-commit hooks enforce linting, formatting, type checking, and secrets detection automatically on each commit.

## Code Standards

- Python >=3.11
- Google-style docstrings on all public functions and classes
- Type hints on all function signatures
- 100 character line length (ruff)

## Testing

- Framework: pytest
- Test files mirror source structure under `tests/`

## License

By contributing, you agree that your contributions will be licensed under MIT.
```

**Step 4: Commit**

```bash
git add LICENSE SECURITY.md CONTRIBUTING.md
git commit -m "docs: add LICENSE (MIT), SECURITY.md, CONTRIBUTING.md"
```

---

## Task 11: AI-STATEMENT.md Update + CLAUDE.md

**Files:**
- Modify: `AI-STATEMENT.md` (verify no Volery refs — already clean)
- Create: `CLAUDE.md` (rewrite completely)

**Step 1: Verify AI-STATEMENT.md**

Read the file — confirm no Volery references. The current content is generic and doesn't mention Volery, so it should be clean. No changes needed.

**Step 2: Write CLAUDE.md**

Follow counteragent's structure and adapt for countersignal:

```markdown
# countersignal

Agentic AI content & supply chain attack toolkit. Monorepo consolidating IPI-Canary, CXP-Canary, and future RXP into one Python package with a unified CLI. CounterSignal is the content & supply chain arm of the Agentic AI Security ecosystem. The sister program CounterAgent handles protocol & system security (MCP auditing, traffic interception).

## Project Layout

```
src/countersignal/
├── __init__.py               # Package version
├── __main__.py               # python -m countersignal support
├── cli.py                    # Root Typer app — mounts ipi, cxp, rxp
├── core/                     # Shared infrastructure: callback tracking, storage, evidence
│   ├── models.py             # Shared data models for callback tracking
│   ├── listener.py           # Callback listener server
│   ├── db.py                 # Campaign and hit storage
│   └── evidence.py           # Shared evidence collection patterns
├── ipi/                      # Indirect prompt injection (from IPI-Canary)
│   └── cli.py                # ipi subcommand CLI
├── cxp/                      # Context file poisoning (from CXP-Canary)
│   └── cli.py                # cxp subcommand CLI
└── rxp/                      # RAG retrieval poisoning [planned]
    └── cli.py                # rxp subcommand CLI
tests/                        # Test suite mirroring src/ structure
harness/                      # Live test harnesses (IPI arrives Phase C)
```

## Code Standards

- **Python:** >=3.11
- **Docstrings:** Google-style on all public functions and classes
- **Type hints:** Required on all function signatures
- **Line length:** 100 chars (ruff)
- **Imports:** Sorted by ruff (isort rules)

## CLI Usage

```bash
# Top-level help
countersignal --help

# Subcommands
countersignal ipi --help
countersignal cxp --help
countersignal rxp --help
```

Smoke tests after changes:
```bash
countersignal --help
countersignal ipi --help
countersignal cxp --help
```

## Testing

- Framework: pytest
- Test files mirror source structure under `tests/`
- **All tests must pass before committing**

Run tests:
```bash
uv run pytest -q
```

## Git Workflow

**Never commit directly to main.** Branch protection enforced.

```bash
git checkout main && git pull
git checkout -b feature/description
# ... work ...
uv run pytest -q
countersignal --help
git add .
git commit -F .commitmsg
git push -u origin feature/description
```

### Shell Quoting (CRITICAL)

CMD corrupts `git commit -m "message with spaces"`. Always use:
```bash
echo "feat: description here" > .commitmsg
git commit -F .commitmsg
del .commitmsg
```

### End of Session

Commit to branch, `git stash -m "description"`, or `git restore .` — never leave uncommitted changes.

## Pre-commit Hooks

Hooks run automatically on `git commit`:
- trailing-whitespace, end-of-file-fixer, check-yaml, check-toml
- check-added-large-files, check-merge-conflict
- **no-commit-to-branch** (blocks direct commits to main)
- **ruff-check** (lint + auto-fix) + **ruff-format**
- **gitleaks** (secrets detection)
- **mypy** (type checking)

If pre-commit fails, fix issues and re-stage before committing.

## Dependencies

Managed via `uv` with PEP 735 dependency groups. Sync with:
```bash
uv sync --group dev
```

**Without `--group dev`, dev dependencies get stripped.**

## Build

- `src/` layout with `hatchling` backend
- Entry point: `countersignal = "countersignal.cli:app"`
- Packaging: `uv` with PEP 735 dependency groups

## Claude Code Guardrails

### Verification Scope
- Run only the tests for new/changed code, not the full suite
- Smoke test the CLI after changes (`countersignal --help`)
- Full suite verification is the developer's responsibility before merging

### Timeout Policy
- If any test run exceeds 60 seconds, stop and identify the stuck test
- Do not set longer timeouts and wait — diagnose instead

### Process Hygiene
- Before running tests, kill any orphaned python/node processes from previous runs

### Failure Mode
- If verification hits a problem you can't resolve in 2 attempts, commit the work to the branch and report what failed
- Do not spin on the same failure

### Boundaries
- Do not create PRs. Push the branch and stop.
- Do not attempt to install CLI tools (gh, hub, etc.)
- Do not modify files in `concepts/` or `docs/` unless the task brief explicitly says to

## Session Discipline

Before committing, run:
```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src/countersignal/
```

## Legal & Ethical

- Only test systems you own, control, or have explicit permission to test
- Responsible disclosure for all vulnerabilities
- Frame all tooling as defensive security testing tools
```

**Step 3: Commit**

```bash
git add CLAUDE.md AI-STATEMENT.md
git commit -m "docs: add CLAUDE.md project guide, verify AI-STATEMENT.md"
```

---

## Task 12: README.md

**Files:**
- Create: `README.md`

**Step 1: Write README.md**

```markdown
# CounterSignal

**Agentic AI content & supply chain attack toolkit.**

CounterSignal consolidates three content-layer security testing tools into a single Python package with a unified CLI. Each module targets a different attack surface where AI agents ingest external content — documents, project files, and vector databases. The shared methodology across all modules is generate, deploy, and track execution via out-of-band callback. A callback proves the agent *acted*, not just that it *responded*.

> Research program by [Richard Spicer](https://richardspicer.io) · [GitHub](https://github.com/richardspicer)

---

## Modules

### IPI — Indirect Prompt Injection

Generate documents with hidden payloads across multiple formats (PDF, Image, Markdown, HTML, DOCX, ICS, EML) and track execution via authenticated callbacks. Tests whether AI agents execute injected instructions when ingesting documents.

### CXP — Context File Poisoning

Test whether poisoned project-level instruction files (CLAUDE.md, .cursorrules, copilot-instructions.md, etc.) cause AI coding assistants to produce vulnerable code, exfiltrate data, or execute commands.

### RXP — RAG Retrieval Poisoning *(planned)*

Generate documents optimized to win vector similarity battles in RAG systems, guaranteeing that poisoned content reaches the LLM context window. The missing first half of the RAG attack chain.

---

## Quick Start

**Development install:**

```bash
git clone https://github.com/richardspicer/countersignal.git
cd countersignal
uv sync --group dev
```

```bash
countersignal --help
countersignal ipi --help
countersignal cxp --help
countersignal rxp --help
```

> CounterSignal is not yet published to PyPI. Install from source for now.

---

## Sister Project

**[CounterAgent](https://github.com/richardspicer/counteragent)** — the protocol & system security arm of the Agentic AI Security ecosystem. MCP server auditing, traffic interception, and agent attack chain testing.

## Framework Mapping

| Module | OWASP LLM Top 10 (2025) | OWASP Agentic Top 10 (2026) |
|--------|--------------------------|----------------------------|
| **IPI** | LLM01: Prompt Injection | ASI-01: Agent Goal Hijacking |
| **CXP** | LLM01, LLM03: Supply Chain | ASI-01, ASI-03: Tool Misuse |
| **RXP** | LLM08: Vector & Embedding Weaknesses | ASI-07: Knowledge Poisoning |

## Legal

All tools are intended for authorized security testing only. Only test systems you own, control, or have explicit permission to test. Responsible disclosure for all vulnerabilities discovered.

## AI Disclosure

This project uses a human-led, AI-augmented workflow. See [AI-STATEMENT.md](AI-STATEMENT.md).

## License

[MIT](LICENSE)
```

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add README.md for countersignal monorepo"
```

---

## Task 13: Docs Directory

**Files:**
- Create: `docs/Architecture.md`
- Create: `docs/owasp_mapping.md`
- Modify: `docs/Roadmap.md` (already moved in Task 2 — verify Volery refs are fixed)
- Verify: `docs/Architecture-Decision.md` exists (already present)

**Step 1: Write Architecture.md placeholder**

```markdown
# Architecture

Architecture documentation will be written after migration is complete. See [Architecture-Decision.md](Architecture-Decision.md) for migration design.
```

**Step 2: Write owasp_mapping.md placeholder**

```markdown
# OWASP Mapping

OWASP mapping for content attack categories — planned.
```

**Step 3: Verify Roadmap.md Volery refs are updated**

Check `docs/Roadmap.md` for any remaining "Volery" references beyond the one fixed in Task 2. The Roadmap is long — search and replace all remaining instances.

```bash
grep -n "Volery\|volery" docs/Roadmap.md
```

If any remain, update them to "CounterSignal".

**Step 4: Commit**

```bash
git add docs/
git commit -m "docs: add Architecture.md and owasp_mapping.md placeholders"
```

---

## Task 14: Harness Directory

**Files:**
- Create: `harness/.gitkeep`

**Step 1: Create harness directory with .gitkeep**

```bash
mkdir -p harness
touch harness/.gitkeep
```

**Step 2: Commit**

```bash
git add harness/
git commit -m "chore: add empty harness directory for future test harnesses"
```

---

## Task 15: Full Verification — All Acceptance Criteria

Run every acceptance criterion from the task brief. Do NOT commit — just verify.

**Step 1: uv sync**

```bash
uv sync --group dev
```
Expected: succeeds without errors.

**Step 2: CLI verification**

```bash
uv run countersignal --help
uv run countersignal ipi --help
uv run countersignal cxp --help
uv run countersignal rxp --help
uv run python -m countersignal --help
```
Expected: all show appropriate help text.

**Step 3: Linting**

```bash
uv run ruff check .
uv run ruff format --check .
```
Expected: both pass clean.

**Step 4: Type checking**

```bash
uv run mypy src/countersignal/
```
Expected: passes clean.

**Step 5: Tests**

```bash
uv run pytest -q
```
Expected: exit code 5 (no tests collected) — acceptable.

**Step 6: Pre-commit**

```bash
uv run pre-commit install
uv run pre-commit run --all-files
```
Expected: all hooks pass.

**Step 7: Verify standard docs exist**

```bash
ls CLAUDE.md SECURITY.md CONTRIBUTING.md AI-STATEMENT.md LICENSE README.md
```
Expected: all six files listed.

**Step 8: Verify CI workflows exist**

```bash
ls .github/workflows/ci.yml .github/workflows/codeql.yml
```
Expected: both files listed.

**Step 9: Verify no stale references**

```bash
grep -ri "volery\|ipi-canary\|cxp-canary" src/ tests/ CLAUDE.md SECURITY.md CONTRIBUTING.md README.md LICENSE .github/ pyproject.toml .pre-commit-config.yaml .gitignore
```
Expected: no matches. (References in `docs/` and `concepts/` in historical context are OK.)

**Step 10: Build sanity check**

```bash
uv build
```
Expected: produces `.tar.gz` and `.whl` in `dist/`. Verify the wheel contains `countersignal/` package.

**Step 11: If any check fails**

Fix the issue, re-stage, and create a fixup commit. Then re-run the failing check. Do not proceed to push until all checks pass.

---

## Task 16: Push Branch

**Step 1: Push to remote**

```bash
git push -u origin feature/scaffold-monorepo
```

**Do NOT create a PR.** Push the branch and stop (per CLAUDE.md guardrails).

---

## Summary of Commits

| Task | Commit Message |
|------|---------------|
| 1 | `chore: add Python .gitignore` |
| 2 | `chore: reorganize existing content for monorepo scaffold` |
| 3+4 | `feat: add package structure with Typer CLI stubs` |
| 5 | `feat: add pyproject.toml with merged dependencies` |
| 7 | `chore: add empty test directory structure` |
| 8 | `chore: add pre-commit config` |
| 9 | `ci: add CI and CodeQL workflows` |
| 10 | `docs: add LICENSE (MIT), SECURITY.md, CONTRIBUTING.md` |
| 11 | `docs: add CLAUDE.md project guide, verify AI-STATEMENT.md` |
| 12 | `docs: add README.md for countersignal monorepo` |
| 13 | `docs: add Architecture.md and owasp_mapping.md placeholders` |
| 14 | `chore: add empty harness directory for future test harnesses` |
