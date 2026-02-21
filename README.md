# Volery

**Open source offensive security suite for testing content and supply chain attacks against AI agents.**

> **Status:** IPI-Canary is the first released tool. CXP-Canary (Phase 1.5) and Drongo (Phase 2.5) are planned.

A flock of birds — sentinel tools (canaries) that detect agent compromise via out-of-band callback, and ecological attack tools that simulate invasive behaviors in AI knowledge systems. Covers indirect prompt injection, coding assistant context poisoning, and RAG retrieval poisoning.

> Research program by [Richard Spicer](https://richardspicer.io) · [GitHub](https://github.com/richardspicer)

Volery is the **content & supply chain** arm of the Agentic AI Security ecosystem. The **CounterAgent** program ([mcp-audit](https://github.com/richardspicer/mcp-audit), mcp-proxy, agent-inject, agent-chain) is the sister program handling protocol & system security.

---

## Tools

The program produces three tools in phases, each targeting a different content-based attack surface:

| Tool | Phase | Focus | Status |
|------|-------|-------|--------|
| [**IPI-Canary**](https://github.com/richardspicer/IPI-Canary) | 1 | Indirect prompt injection via document ingestion — proof-of-execution callback tracking | 🟢 v0.1.0 |
| **CXP-Canary** | 1.5 | Coding assistant context poisoning — test whether project instruction files cause vulnerable code generation | 📋 Planned |
| **Drongo** | 2.5 | RAG retrieval poisoning optimizer — generate documents that win vector similarity battles to guarantee payload retrieval | 📋 Planned |

---

Existing AI red teaming tools (Garak, PyRIT, Promptfoo, Spikee) focus on LLM-level testing — prompt injection, output analysis, jailbreaks. Volery targets the content layer: what happens when AI agents ingest documents, parse project files, or retrieve poisoned content from vector databases. The shared methodology across all three tools is generate → deploy → track execution via callback.

---

## Phase 1: Indirect Prompt Injection Detection — `IPI-Canary` (Active)

The anchor tool. Generates documents with hidden payloads across 7 formats (PDF, Image, Markdown, HTML, DOCX, ICS, EML) using 34 hiding techniques and listens for callbacks when AI agents execute them. Authenticated callbacks with confidence scoring provide proof-of-execution.

```bash
# Generate payloads (all formats, all techniques)
ipi-canary generate --callback http://your-server:8080 --output ./payloads/ --technique all --payload citation

# Start listener (binds to localhost by default; use --host 0.0.0.0 for remote callbacks)
ipi-canary listen --host 0.0.0.0 --port 8080

# Check results
ipi-canary status
```

**Current status:** 34 techniques across 7 formats, 7 payload styles × 7 payload types (49 template combinations), authenticated callbacks with confidence scoring, HTMX web dashboard, deterministic corpus generation. 12 confirmed real-world callbacks against Open WebUI. 18 models tested across Ollama, Groq, and OpenRouter. See the [IPI-Canary repo](https://github.com/richardspicer/IPI-Canary) for details.

---

## Phase 1.5: Coding Assistant Context Poisoning — `CXP-Canary` (Planned)

Tests whether poisoned project-level instruction files (CLAUDE.md, AGENTS.md, .cursorrules, copilot-instructions.md, .windsurfrules, .gemini/settings.json) cause AI coding assistants to produce vulnerable code, exfiltrate data, or execute commands.

- Generate poisoned context file corpora organized by objective (backdoor insertion, credential exfil, dependency confusion, permission escalation) and by assistant format
- Test against real coding assistants: Claude Code, Cursor, GitHub Copilot, Windsurf, Codex
- Produce assistant comparison matrices showing susceptibility by payload category
- Generate bounty-ready PoCs: minimal reproduction packages (poisoned repo + trigger prompt + evidence capture)

Completely unoccupied niche — academic research catalogs 42+ attack techniques but no packaged offensive testing tool exists.

---

## Phase 2.5: RAG Retrieval Poisoning Optimizer — `Drongo` (Planned)

Extends IPI-Canary into contested retrieval scenarios: IPI-Canary proves execution once content is retrieved; Drongo tests whether poisoned content can win the vector similarity battle against legitimate documents to reach the LLM's context window. Named after the fork-tailed drongo — an African bird that mimics alarm calls to manipulate other species' behavior and steal their food. Drongo generates documents optimized to win vector similarity battles in RAG systems.

- Generate text optimized for high cosine similarity with likely user queries across common embedding models
- Wrap optimized text + injection payload into document formats (PDF, DOCX, TXT, HTML)
- Validate retrieval rank against test vector DB (ChromaDB)
- Report retrieval success rates across embedding models

Natural pairing with IPI-Canary: Drongo optimizes for retrieval → IPI-Canary wraps with callback payloads → combined tool tests the full RAG attack chain.

---

## The Shared Methodology

All three tools follow the same pattern:

1. **Generate** — Create payloads tailored to the target attack surface
2. **Deploy** — Place payloads where AI agents will ingest them
3. **Track** — Listen for out-of-band callbacks proving execution
4. **Evidence** — Capture proof-of-execution with metadata for research, bounties, and disclosure

This is what separates Volery from output analysis tools. A callback proves the agent *acted*, not just that it *responded*.

---

## Framework Mapping

Each tool maps to established AI security frameworks:

| Tool | OWASP LLM Top 10 (2025) | OWASP Agentic Top 10 (2026) | MITRE ATLAS |
|------|--------------------------|----------------------------|-------------|
| **IPI-Canary** | LLM01: Prompt Injection | ASI-01: Agent Goal Hijacking | AML.T0051: LLM Prompt Injection |
| **CXP-Canary** | LLM01: Prompt Injection, LLM03: Supply Chain | ASI-01: Agent Goal Hijacking, ASI-03: Tool Misuse | AML.T0051: LLM Prompt Injection |
| **Drongo** | LLM08: Vector & Embedding Weaknesses | ASI-07: Knowledge Poisoning | AML.T0020: Poison Training Data |

**LLM01 (Prompt Injection)** — IPI-Canary and CXP-Canary both exploit indirect prompt injection through different delivery vectors (documents vs context files).

**LLM08 (Vector & Embedding Weaknesses)** — Added in the 2025 revision specifically for RAG poisoning. Drongo targets this directly by optimizing content for retrieval ranking manipulation.

**ASI-01 (Agent Goal Hijacking)** — All three tools ultimately aim to hijack agent behavior via content ingestion.

**ASI-07 (Knowledge Poisoning)** — Drongo's primary target: corrupting the knowledge base the agent retrieves from.

---

## Legal

All tools are intended for authorized security testing only. Only test systems you own, control, or have explicit permission to test. Responsible disclosure for all vulnerabilities discovered.

## License

All Volery tools are released under [MIT](https://opensource.org/licenses/MIT).

## Documentation

| Document | Purpose |
|----------|---------|
| [Roadmap](Roadmap.md) | Phased development plan, tool descriptions, success metrics |
| [Architecture](Architecture.md) | Program-level architecture notes and cross-tool integration points |
| [concepts/](concepts/) | Concept docs for planned tools (CXP-Canary, Drongo) |

## AI Disclosure

This project uses a human-led, AI-augmented workflow. See [AI-STATEMENT.md](AI-STATEMENT.md).
