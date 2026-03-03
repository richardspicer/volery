# CounterSignal
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Docs](https://img.shields.io/badge/docs-countersignal.dev-8b5cf6)](https://docs.countersignal.dev)

**Agentic AI content & supply chain attack toolkit.**

CounterSignal consolidates three content-layer security testing tools into a single Python package with a unified CLI. Each module targets a different attack surface where AI agents ingest external content — documents, project files, and vector databases. The shared methodology across all modules is generate, deploy, and track execution via out-of-band callback. A callback proves the agent *acted*, not just that it *responded*.

> Research program by [Richard Spicer](https://richardspicer.io) · [GitHub](https://github.com/richardspicer)

## Modules

**IPI — Indirect Prompt Injection:** Generate documents with hidden payloads — 34 hiding techniques across 7 formats (PDF, Image, Markdown, HTML, DOCX, ICS, EML) — and track execution via authenticated callbacks.

**CXP — Context File Poisoning:** Test whether poisoned project-level instruction files cause AI coding assistants to produce vulnerable code, exfiltrate data, or execute commands. 2 attack objectives across 3 assistant formats.

**RXP — RAG Retrieval Poisoning *(planned)*:** Generate documents optimized to win vector similarity battles in RAG systems, guaranteeing that poisoned content reaches the LLM context window.

## Quick Start

```bash
git clone https://github.com/q-uestionable-AI/countersignal.git
cd countersignal
uv sync --group dev
```

> CounterSignal is not yet published to PyPI. Install from source for now.

## Usage Examples

```bash
# IPI — Generate payloads and track execution
countersignal ipi generate --callback http://localhost:8080 --technique all
countersignal ipi listen --port 8080
countersignal ipi status

# CXP — Test coding assistant context poisoning
countersignal cxp generate --objective backdoor --format claude_md
countersignal cxp report matrix --format markdown
```

## Sister Project

**[CounterAgent](https://github.com/q-uestionable-AI/counteragent)** — the protocol & system security arm of the Agentic AI Security ecosystem. MCP server auditing, traffic interception, and agent attack chain testing.

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
