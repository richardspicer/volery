# countersignal

Agentic AI content & supply chain attack toolkit. Monorepo with IPI, CXP, and RXP modules in one Python package with a unified CLI. CounterSignal is the content & supply chain arm of the Agentic AI Security ecosystem. The sister program CounterAgent handles protocol & system security (MCP auditing, traffic interception).

## Project Layout

```
src/countersignal/
├── __init__.py               # Package version
├── __main__.py               # python -m countersignal support
├── cli.py                    # Root Typer app — mounts ipi, cxp, rxp
├── core/                     # Shared infrastructure: callback tracking, storage, evidence
│   ├── models.py             # Campaign, Hit, HitConfidence (Pydantic)
│   ├── listener.py           # Callback confidence scoring
│   ├── db.py                 # SQLite campaign/hit storage (~/.countersignal/ipi.db)
│   └── evidence.py           # Shared evidence collection patterns (stub)
├── ipi/                      # Indirect prompt injection
│   └── cli.py                # ipi subcommand CLI
├── cxp/                      # Context file poisoning
│   └── cli.py                # cxp subcommand CLI
└── rxp/                      # RAG retrieval poisoning [planned]
    └── cli.py                # rxp subcommand CLI
tests/                        # Test suite mirroring src/ structure
harness/                      # Live test harnesses
```

## Database Locations

- IPI: `~/.countersignal/ipi.db` (shared core/db.py)
- CXP: `~/.countersignal/cxp.db` (cxp/evidence.py)

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
