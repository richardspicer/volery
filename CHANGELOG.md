# Changelog

All notable changes to CounterSignal will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [0.1.0] - 2026-03-04

### Added
- Unified monorepo consolidating IPI, CXP, and RXP modules into a single `countersignal` package
- Unified CLI: `countersignal ipi`, `countersignal cxp`, `countersignal rxp`
- Shared callback infrastructure in `core/` (models, db, listener)
- Centralized DB storage in `~/.countersignal/` (ipi.db, cxp.db)

#### IPI Module
- 34 payload techniques across 7 document formats (PDF, DOCX, Markdown, HTML, iCal, EXIF, plain text)
- 7 injection types including exfil, RCE, pivot, persistence, and social engineering variants
- Authenticated callback tracking with HMAC-signed tokens
- Web dashboard for live callback monitoring and payload management
- Deterministic seeding for reproducible test campaigns
- `ipi generate`, `ipi serve`, `ipi listen`, `ipi list-techniques` CLI commands

#### CXP Module
- 5 objectives × 6 context file formats = 30 techniques
- Objectives: backdoor insertion, data exfiltration, dependency confusion, privilege escalation,
  command execution
- Formats: AGENTS.md, GEMINI.md, .windsurfrules, .cursorrules, CLAUDE.md,
  .github/copilot-instructions.md
- Full builder/reporter/validator pipeline

#### RXP Module
- Embedding model registry with 3 supported models
- ChromaDB collection management for poisoned document sets
- Retrieval validation engine to confirm poisoned documents surface in queries
- HR policy domain profile for realistic RAG poisoning scenarios
- Arbitrary HuggingFace model names accepted
- Optional dependency install via `countersignal[rxp]`
- `rxp list-models`, `rxp list-profiles`, `rxp validate` CLI commands

#### Documentation
- Mintlify docs site at [docs.countersignal.dev](https://docs.countersignal.dev) — 24 pages
- IPI, CXP, and RXP module documentation with CLI references
- Demo GIF

#### Infrastructure
- Pre-commit hooks: ruff, mypy, gitleaks, trailing whitespace
- CI pipeline: lint/format/typecheck/test matrix on Ubuntu + Windows (Python 3.11–3.13)
- `security-scan` job: bandit SAST + pip-audit dependency audit
- CodeQL enabled
- 136+ tests across IPI, CXP, and RXP modules

### Changed
- IPI source migrated to `src/countersignal/ipi/`
- CXP source migrated to `src/countersignal/cxp/` with Click-to-Typer conversion
- CXP database moved from working directory to `~/.countersignal/cxp.db`
- IPI database moved from `~/.countersignal/canary.db` to `~/.countersignal/ipi.db`

### Removed
- Separate standalone CLI entry points (replaced by `countersignal ipi` and `countersignal cxp`)
- Click dependency (CXP converted to Typer)

[0.1.0]: https://github.com/q-uestionable-AI/countersignal/releases/tag/v0.1.0
