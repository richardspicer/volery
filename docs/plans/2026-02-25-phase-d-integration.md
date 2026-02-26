# Phase D: Integration & Cleanup — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Turn two migrated tools into one coherent package — fix DB paths, clean stale references, rewrite docs, and verify everything works.

**Architecture:** Core extraction (IPI callback infra → core/) was already done in Phase C. Phase D finishes the job: rename `canary.db` → `ipi.db`, move CXP's DB to `~/.countersignal/cxp.db`, sweep stale references to old repo names, rewrite all docs for the monorepo, and add pytest-timeout. No structural changes to core/ — it's already correct.

**Tech Stack:** Python 3.11+, uv, pytest, ruff, mypy, Typer CLI

---

## Task 1: Create Feature Branch

**Files:** None

**Step 1: Create branch from main**

```bash
git checkout main && git pull
git checkout -b feature/phase-d-integration
```

**Step 2: Verify clean state**

Run: `git status`
Expected: Clean working tree on feature/phase-d-integration

---

## Task 2: Rename IPI DB Path from canary.db to ipi.db

The task brief specifies `~/.countersignal/ipi.db` for IPI and `~/.countersignal/cxp.db` for CXP. Currently `core/db.py` uses `~/.countersignal/canary.db`.

**Files:**
- Modify: `src/countersignal/core/db.py:31-32` (DEFAULT_DB_PATH and docstring)
- Modify: `src/countersignal/core/db.py:14` (module docstring)
- Modify: `src/countersignal/core/db.py:48` (get_connection docstring)
- Test: `tests/ipi/test_db_init.py`

**Step 1: Update DEFAULT_DB_PATH in core/db.py**

Change line 31:
```python
DEFAULT_DB_PATH = Path.home() / ".countersignal" / "ipi.db"
```
Update the inline docstring on line 32:
```python
"""Default database file location (~/.countersignal/ipi.db)."""
```
Update module docstring reference from `canary.db` to `ipi.db`.
Update `get_connection` docstring reference from `canary.db` to `ipi.db`.

**Step 2: Run IPI tests**

Run: `uv run pytest tests/ipi/ -v`
Expected: All 3 IPI tests pass. Tests use tmp paths so they won't care about the default.

**Step 3: Commit**

```bash
echo "refactor: rename IPI default DB from canary.db to ipi.db" > .commitmsg && git add src/countersignal/core/db.py && git commit -F .commitmsg && del .commitmsg
```

---

## Task 3: Move CXP DB Path to ~/.countersignal/cxp.db

CXP currently defaults to `./cxp-canary.db` in the working directory. Move to `~/.countersignal/cxp.db` and add parent directory creation.

**Files:**
- Modify: `src/countersignal/cxp/evidence.py:13` (_DEFAULT_DB_PATH)
- Modify: `src/countersignal/cxp/evidence.py:41-53` (get_db — add mkdir)
- Modify: `src/countersignal/cxp/evidence.py:45` (docstring)
- Modify: `src/countersignal/cxp/cli.py:97,162,233,286,321` (5 help text strings)
- Test: `tests/cxp/` (all CXP tests)

**Step 1: Update _DEFAULT_DB_PATH in evidence.py**

Change line 13:
```python
_DEFAULT_DB_PATH = Path.home() / ".countersignal" / "cxp.db"
```

**Step 2: Add parent directory creation to get_db()**

In `get_db()`, after `path = db_path or _DEFAULT_DB_PATH`, add:
```python
path.parent.mkdir(parents=True, exist_ok=True)
```

Update the docstring from `./cxp-canary.db` to `~/.countersignal/cxp.db`.

**Step 3: Update CLI help text strings**

In `src/countersignal/cxp/cli.py`, change all 5 occurrences of:
```
"Database path (default: ./cxp-canary.db)."
```
to:
```
"Database path (default: ~/.countersignal/cxp.db)."
```

These are on lines 97, 162, 233, 286, 321.

**Step 4: Run CXP tests**

Run: `uv run pytest tests/cxp/ -v`
Expected: All 97 CXP tests pass. Tests that use DB should create tmp paths or use the default (which now creates dirs automatically).

**Step 5: Commit**

```bash
echo "refactor: move CXP DB to ~/.countersignal/cxp.db" > .commitmsg && git add src/countersignal/cxp/evidence.py src/countersignal/cxp/cli.py && git commit -F .commitmsg && del .commitmsg
```

---

## Task 4: Fix Stale References in Source Code

Sweep `.py` source files for old repo/tool names and update them. Do NOT touch `docs/Architecture-Decision.md` (historical document) or `docs/plans/` (historical).

**Files:**
- Modify: `src/countersignal/cxp/builder.py:102,108` — change `CXP-Canary` to `CounterSignal CXP`
- Modify: `src/countersignal/ipi/generators/image.py:215` — change `b"IPI-Canary"` to `b"CounterSignal"`
- Modify: `src/countersignal/ipi/generators/pdf.py:3` — change docstring reference from `IPI-Canary` to `CounterSignal IPI`
- Modify: `harness/README.md` — update all `ipi-canary` CLI examples to `countersignal ipi`
- Modify: `harness/harness.py` — update `IPI-Canary Test Harness` references to `CounterSignal IPI Test Harness`

**Step 1: Fix CXP builder.py**

In `_generate_readme()`, change `CXP-Canary Test Repository` to `CounterSignal CXP Test Repository` and `CXP-Canary, a context poisoning tester` to `CounterSignal CXP, a context poisoning tester`.

**Step 2: Fix IPI image.py EXIF Software field**

Change `piexif.ImageIFD.Software: b"IPI-Canary"` to `piexif.ImageIFD.Software: b"CounterSignal"`.

**Step 3: Fix IPI pdf.py docstring**

Change `for IPI-Canary:` to `for CounterSignal IPI:` in the module docstring.

**Step 4: Fix harness/README.md**

Replace all `ipi-canary` command references with `countersignal ipi`. Replace `IPI-Canary` with `CounterSignal IPI` in title and prose. Update `cd IPI-Canary` to `cd countersignal`.

**Step 5: Fix harness/harness.py**

Replace `IPI-Canary Test Harness` with `CounterSignal IPI Test Harness` in docstrings/strings.

**Step 6: Verify no remaining stale references in src/**

Run: `grep -r "ipi.canary\|cxp.canary\|IPI-Canary\|CXP-Canary\|ipi_canary\|cxp_canary" src/`
Expected: No matches (or only in string constants that are intentional).

Run: `grep -ri "volery" src/`
Expected: No matches.

**Step 7: Run full test suite**

Run: `uv run pytest -q`
Expected: 104 tests pass.

**Step 8: Commit**

```bash
echo "fix: replace stale IPI-Canary/CXP-Canary references with CounterSignal" > .commitmsg && git add -A && git commit -F .commitmsg && del .commitmsg
```

---

## Task 5: Add pytest-timeout

**Files:**
- Modify: `pyproject.toml` (add pytest-timeout to dev deps + ini_options)

**Step 1: Add pytest-timeout to dev dependency group**

Add `"pytest-timeout>=2.3.0",` to `[dependency-groups] dev`.

**Step 2: Add timeout to pytest config**

In `[tool.pytest.ini_options]`, add:
```toml
timeout = 60
```

**Step 3: Sync dependencies**

Run: `uv sync --group dev`
Expected: pytest-timeout installed.

**Step 4: Run tests with timeout active**

Run: `uv run pytest -q`
Expected: 104 tests pass, none timeout.

**Step 5: Commit**

```bash
echo "feat: add pytest-timeout with 60s default" > .commitmsg && git add pyproject.toml uv.lock && git commit -F .commitmsg && del .commitmsg
```

---

## Task 6: Lint & Type Check Pass

**Files:** Various (drive-by fixes)

**Step 1: Run ruff check**

Run: `uv run ruff check .`
Expected: Clean (or fixable issues).

**Step 2: Auto-fix any ruff issues**

Run: `uv run ruff check --fix .`

**Step 3: Run ruff format check**

Run: `uv run ruff format --check .`
If issues: `uv run ruff format .`

**Step 4: Run mypy**

Run: `uv run mypy src/countersignal/`
Expected: Clean or only pre-existing issues.

**Step 5: Run full test suite**

Run: `uv run pytest -q`
Expected: 104 tests pass.

**Step 6: Commit if any fixes were made**

```bash
echo "style: lint and format fixes for Phase D" > .commitmsg && git add -A && git commit -F .commitmsg && del .commitmsg
```

---

## Task 7: Create CHANGELOG.md

**Files:**
- Create: `CHANGELOG.md`

**Step 1: Write CHANGELOG.md**

```markdown
# Changelog

All notable changes to CounterSignal will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [0.1.0] - 2026-02-25

### Added
- Unified monorepo consolidating IPI-Canary and CXP-Canary into a single `countersignal` package
- Unified CLI: `countersignal ipi`, `countersignal cxp`, `countersignal rxp` (stub)
- Shared callback infrastructure in `core/` (models, db, listener)
- Centralized DB storage in `~/.countersignal/` (ipi.db, cxp.db)
- Pre-commit hooks: ruff, mypy, gitleaks, trailing whitespace
- 104 tests across IPI (3) and CXP (97) modules with 4 conftest fixtures

### Changed
- IPI-Canary source migrated to `src/countersignal/ipi/`
- CXP-Canary source migrated to `src/countersignal/cxp/` with Click→Typer conversion
- CXP database moved from working directory (`./cxp-canary.db`) to `~/.countersignal/cxp.db`
- IPI database moved from `~/.countersignal/canary.db` to `~/.countersignal/ipi.db`

### Removed
- Separate `ipi-canary` and `cxp-canary` CLI entry points (replaced by `countersignal ipi` and `countersignal cxp`)
- Click dependency (CXP converted to Typer)
```

**Step 2: Commit**

```bash
echo "docs: add CHANGELOG.md documenting monorepo migration" > .commitmsg && git add CHANGELOG.md && git commit -F .commitmsg && del .commitmsg
```

---

## Task 8: Rewrite Docs — README.md

The existing README.md is already quite good for the monorepo. Minor updates needed:
- Add IPI and CXP CLI usage examples (generate, listen, validate)
- Add test/dev commands section
- Update module descriptions with current capabilities

**Files:**
- Modify: `README.md`

**Step 1: Update README.md**

Keep the existing structure but enhance with:
- CLI usage examples for each module (not just `--help`)
- Development section (test, lint, type check commands)
- Current module status (IPI v1.0 released, CXP pre-alpha, RXP planned)

**Step 2: Commit**

```bash
echo "docs: enhance README with CLI examples and dev workflow" > .commitmsg && git add README.md && git commit -F .commitmsg && del .commitmsg
```

---

## Task 9: Rewrite Docs — Architecture.md

Currently a stub placeholder. Needs full rewrite describing actual post-extraction structure.

**Files:**
- Modify: `docs/Architecture.md`

**Step 1: Write Architecture.md**

Cover:
- Package structure diagram (src/countersignal/ tree)
- Core module: models (Campaign, Hit, HitConfidence), db (SQLite CRUD), listener (confidence scoring)
- IPI module: 34 techniques × 7 formats, generate service, FastAPI dashboard, callback server
- CXP module: objectives × formats matrix, builder, validator, evidence store (separate SQLite)
- RXP module: stub only
- Data flow diagrams: IPI generate→deploy→callback, CXP generate→test→validate
- DB architecture: two separate SQLite files in ~/.countersignal/
- CLI hierarchy: countersignal → ipi/cxp/rxp subcommands

**Step 2: Commit**

```bash
echo "docs: write Architecture.md for monorepo structure" > .commitmsg && git add docs/Architecture.md && git commit -F .commitmsg && del .commitmsg
```

---

## Task 10: Rewrite Docs — Roadmap.md

Update to use CounterSignal module names instead of old tool names.

**Files:**
- Modify: `docs/Roadmap.md`

**Step 1: Update Roadmap.md**

- Change `IPI-Canary` → `IPI` throughout (it's a module now, not a standalone tool)
- Change `CXP-Canary` → `CXP` throughout
- Change `Drongo` → `RXP` in section headers (keep Drongo as codename in description)
- Update build sequence diagram to show monorepo phases
- Keep all research content intact — only rename references

**Step 2: Commit**

```bash
echo "docs: update Roadmap.md with monorepo module names" > .commitmsg && git add docs/Roadmap.md && git commit -F .commitmsg && del .commitmsg
```

---

## Task 11: Update CLAUDE.md

The current CLAUDE.md is mostly correct for the monorepo. Update to reflect Phase D changes (DB paths, core extraction status).

**Files:**
- Modify: `CLAUDE.md`

**Step 1: Update CLAUDE.md**

Changes needed:
- Update project layout to show `core/` contains models.py, db.py, listener.py (not just stubs)
- Remove `ipi/db.py` from layout (doesn't exist — IPI uses core/db.py)
- Add note about DB locations: `~/.countersignal/ipi.db` and `~/.countersignal/cxp.db`
- Update description to not reference "from IPI-Canary" and "from CXP-Canary" — they're CounterSignal modules now

**Step 2: Commit**

```bash
echo "docs: update CLAUDE.md for Phase D structure" > .commitmsg && git add CLAUDE.md && git commit -F .commitmsg && del .commitmsg
```

---

## Task 12: Update CONTRIBUTING.md

Minor updates to reflect monorepo conventions.

**Files:**
- Modify: `CONTRIBUTING.md`

**Step 1: Update CONTRIBUTING.md**

Changes:
- Add `pytest-timeout` mention in testing section
- Add test structure note: tests mirror `src/countersignal/` with `tests/ipi/`, `tests/cxp/`, `tests/core/`
- Add module-specific test commands: `uv run pytest tests/ipi/ -v`, `uv run pytest tests/cxp/ -v`

**Step 2: Commit**

```bash
echo "docs: update CONTRIBUTING.md with module test commands" > .commitmsg && git add CONTRIBUTING.md && git commit -F .commitmsg && del .commitmsg
```

---

## Task 13: Verify pyproject.toml

Check for stale deps, correct entry points, and PEP 735 groups.

**Files:**
- Modify: `pyproject.toml` (if needed)

**Step 1: Verify entry points**

Confirm `[project.scripts]` has only `countersignal = "countersignal.cli:app"`. No `ipi-canary` or `cxp-canary` entries should exist.

**Step 2: Verify dependencies**

Check that all imported packages in src/ have corresponding entries in dependencies. No stale deps that aren't used.

**Step 3: Verify dev group**

Confirm `pytest-timeout` was added in Task 5. Confirm no stale dev deps.

**Step 4: Commit if changes needed**

```bash
echo "chore: clean up pyproject.toml" > .commitmsg && git add pyproject.toml && git commit -F .commitmsg && del .commitmsg
```

---

## Task 14: Stale Reference Sweep in Docs

Search all `.md` files for `ipi-canary`, `cxp-canary`, `volery` references. Fix those that should be updated (skip Architecture-Decision.md and plans/ as historical).

**Files:**
- Possibly modify: `concepts/rxp.md`, `docs/Roadmap.md` (if not fully caught in Task 10)

**Step 1: Search for stale references**

Run: `grep -ri "ipi-canary\|cxp-canary\|volery" *.md docs/*.md concepts/*.md`
Expected: Only Architecture-Decision.md and plans/ files (historical, don't touch).

**Step 2: Fix any found references**

Update `concepts/rxp.md` to use `CounterSignal IPI` instead of `IPI-Canary`.

**Step 3: Commit if changes made**

```bash
echo "docs: sweep remaining stale references in markdown docs" > .commitmsg && git add -A && git commit -F .commitmsg && del .commitmsg
```

---

## Task 15: Final Verification

**Step 1: Full lint pass**

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src/countersignal/
```
Expected: All clean.

**Step 2: Full test suite**

```bash
uv run pytest -q
```
Expected: 104+ tests pass, no timeouts.

**Step 3: CLI smoke tests**

```bash
countersignal --help
countersignal ipi --help
countersignal cxp --help
countersignal rxp --help
countersignal ipi techniques
countersignal ipi formats
```
Expected: All commands respond correctly.

**Step 4: Verify no import errors**

```bash
uv run python -c "from countersignal.core.models import Campaign, Hit, HitConfidence; print('core OK')"
uv run python -c "from countersignal.core.db import DEFAULT_DB_PATH; print(f'IPI DB: {DEFAULT_DB_PATH}')"
uv run python -c "from countersignal.cxp.evidence import _DEFAULT_DB_PATH; print(f'CXP DB: {_DEFAULT_DB_PATH}')"
```
Expected:
- `core OK`
- `IPI DB: C:\Users\richs\.countersignal\ipi.db` (or equivalent)
- `CXP DB: C:\Users\richs\.countersignal\cxp.db` (or equivalent)

**Step 5: Push branch**

```bash
git push -u origin feature/phase-d-integration
```

---

## Out of Scope (Human-Required)

- E2E verification on inference-server (needs lab access at 10.0.40.x)
- PR creation and review
- Merge to main
- Old repo archival (Phase E)

---

## Notes

- **Core extraction is already done.** Phase C moved Campaign/Hit/HitConfidence to core/models.py, db.py to core/db.py, and listener logic to core/listener.py. IPI already imports from core/. This plan does NOT re-extract — it only fixes the DB filename and cleans up.
- **Architecture-Decision.md is a historical document.** Do not update it. It records the decision as it was made.
- **docs/plans/ files are historical.** Do not update them.
- **SECURITY.md and LICENSE need no changes.** Verified — they're already correct for the monorepo.
- **harness/ is in ruff's per-file-ignores.** Harness code changes won't trigger lint failures.
