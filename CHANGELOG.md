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
- 104 tests across IPI and CXP modules

### Changed
- IPI-Canary source migrated to `src/countersignal/ipi/`
- CXP-Canary source migrated to `src/countersignal/cxp/` with Click-to-Typer conversion
- CXP database moved from working directory (`./cxp-canary.db`) to `~/.countersignal/cxp.db`
- IPI database moved from `~/.countersignal/canary.db` to `~/.countersignal/ipi.db`

### Removed
- Separate `ipi-canary` and `cxp-canary` CLI entry points (replaced by `countersignal ipi` and `countersignal cxp`)
- Click dependency (CXP converted to Typer)
