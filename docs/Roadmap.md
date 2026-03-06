## Vision
An offensive security suite for content and supply chain attacks against AI agents — generate payloads, deploy them into AI pipelines, and track execution via out-of-band callback. Proof that agents *acted*, not just that they *responded*.

## Ecosystem Context

CounterSignal is the **content & supply chain** arm of the Agentic AI Security ecosystem under [richardspicer.io](https://richardspicer.io). The **CounterAgent** program is the sister program handling **protocol & system** security — MCP servers, tool trust boundaries, and agent delegation chains.

## The Problem
- AI agents ingest external content from documents, emails, calendars, code repos, and vector databases
- Hidden instructions can hijack agent behavior — producing vulnerable code, exfiltrating data, or executing commands
- Current tools (Garak, PyRIT, Promptfoo, Spikee) analyze LLM output, not agent action
- Coding assistant context files are trusted by default but live in untrusted repos
- RAG retrieval poisoning is a prerequisite for many IPI attacks, but no tool optimizes for it

## The Solution
Three tools targeting three content-based attack surfaces: document ingestion → coding assistant context → RAG retrieval optimization. All share the generate → deploy → track methodology with out-of-band callback verification.

---

## IPI — Indirect Prompt Injection

### Key Design Decisions
- **Callback-based verification** — proof of execution, not output analysis
- **Technique diversity over depth** — cover many hiding methods across many formats to fingerprint parser behavior
- **Authenticated callbacks** — per-campaign cryptographic tokens, HIGH/MEDIUM/LOW confidence scoring
- **Dangerous payload gating** — exfil, SSRF, behavior modification require explicit `--dangerous` flag

### Research
- 12 confirmed real-world callbacks against Open WebUI
- Parser regression: Open WebUI v0.7.2 → v0.8.1 expanded DOCX attack surface
- 18 models tested across Ollama, Groq, and OpenRouter
- Key finding: reasoning models use chain-of-thought to organize compliance, not resist injection

## CXP — Context File Poisoning

CXP tests whether poisoned project-level instruction files cause coding assistants to produce vulnerable code, exfiltrate data, or execute commands. Completely unoccupied niche — academic research catalogs 42 attack techniques but no packaged testing tool exists.

## RXP — RAG Retrieval Poisoning

RXP solves the retrieval prerequisite: guaranteeing poisoned content wins the vector similarity battle. Natural pairing with IPI — RXP optimizes retrieval, IPI wraps with callback payloads, combined documents test retrieve AND execute.

---

## Pre-Release Security Review

| Area | Check |
|------|-------|
| SAST | `ruff` + `mypy` + GitHub CodeQL in CI on every PR |
| CI Matrix | `ubuntu-latest` (Python 3.11/3.13/3.14) + `windows-latest` (Python 3.13 only) |
| Dependencies | GitHub Dependabot |
| Manual | Path traversal, URL validation, input sanitization, error handling |
| Exit Criteria | Zero high/critical CodeQL findings, no known CVEs, SECURITY.md current |

## Ongoing Activities
- **Vulnerability Research:** Multi-platform testing, responsible disclosure, abstract findings to patterns
- **Detection Engineering:** Wazuh and Sigma rules from attack patterns, inference-gateway telemetry
- **Community:** richardspicer.io blog, conference submissions (BSides, DEF CON AI Village)

### Framework Mapping

| Framework | Usage |
|-----------|-------|
| OWASP Top 10 for LLM Applications 2025 | Primary vulnerability taxonomy |
| OWASP Top 10 for Agentic AI | Attack pattern classification |
| MITRE ATLAS | Adversarial ML technique mapping |
| NIST AI RMF | Risk management context |

---

## Success Metrics

**IPI:** 34 techniques × 7 formats, 12 confirmed callbacks, 18 models tested, published parser regression finding, pre-release security review complete. Pending: multi-platform testing.

**CXP:** Poisoned context files cause vulnerable code in 1+ major assistant, comparison matrix covers 3+ assistants, bounty submission, detection rules for poisoning patterns.

**RXP:** Top-3 retrieval rank against target queries, combined RXP + IPI confirmed callbacks, validated across 3+ embedding models.

**Portfolio:** CVE or bounty with name attached, tools other researchers use, conference talk, blog posts that teach something learned the hard way.

## Build Sequence

```text
countersignal (monorepo)
├── core/     Shared callback infrastructure
├── ipi/      Indirect prompt injection detection (v0.1.0 released)
├── cxp/      Coding assistant context poisoning (scaffolded, testing)
└── rxp/      RAG retrieval optimization (v0.1.0 released)
```

## Reference Links
- OWASP Top 10 for LLM Applications 2025: https://owasp.org/www-project-top-10-for-large-language-model-applications/
- OWASP Top 10 for Agentic AI: https://genai.owasp.org/
- MITRE ATLAS: https://atlas.mitre.org/
- Garak: https://github.com/NVIDIA/garak
- PyRIT: https://github.com/Azure/PyRIT
- Spikee: https://github.com/WithSecureLabs/spikee
- Coding Assistant Attack Taxonomy: https://arxiv.org/abs/2601.17548
