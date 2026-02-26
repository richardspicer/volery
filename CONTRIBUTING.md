# Contributing to CounterSignal

## Development Setup

```bash
git clone https://github.com/q-uestionable-AI/countersignal.git
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

## Test Structure

Tests mirror the source layout:

```
tests/
├── conftest.py          # Shared fixtures
├── core/                # Core module tests
├── ipi/                 # IPI module tests
│   ├── test_db_init.py
│   ├── test_path_traversal.py
│   └── test_server_defaults.py
└── cxp/                 # CXP module tests (13 test files)
```

Run module-specific tests:
```bash
uv run pytest tests/ipi/ -v    # IPI tests only
uv run pytest tests/cxp/ -v    # CXP tests only
```

A 60-second timeout (pytest-timeout) is configured globally. If a test hangs, diagnose instead of increasing the timeout.

## License

By contributing, you agree that your contributions will be licensed under MIT.
