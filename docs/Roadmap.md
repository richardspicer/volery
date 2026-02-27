## Vision
An offensive security suite for content and supply chain attacks against AI agents — generate payloads, deploy them into AI pipelines, and track execution via out-of-band callback. Proof that agents *acted*, not just that they *responded*.

---
## Ecosystem Context

CounterSignal is the **content & supply chain** arm of the Agentic AI Security ecosystem under [richardspicer.io](https://richardspicer.io). It tests what happens when AI agents ingest documents, parse project instruction files, or retrieve poisoned content from vector databases.

The **CounterAgent** program (mcp-audit, mcp-proxy, agent-inject, agent-chain) is the sister program handling **protocol & system** security — MCP servers, tool trust boundaries, and agent delegation chains.

---
## The Problem
- AI agents ingest external content from documents, emails, calendars, code repos, and vector databases
- Hidden instructions in that content can hijack agent behavior — producing vulnerable code, exfiltrating data, or executing commands
- Current tools (Garak, PyRIT, Promptfoo, Spikee) analyze LLM output, not agent action
- No automated workflow generates content-layer payloads and tracks proof-of-execution
- Coding assistant context files (CLAUDE.md, AGENTS.md, .cursorrules) are trusted by default but live in untrusted repos
- RAG retrieval poisoning is a prerequisite for many IPI attacks, but no tool optimizes for it

## The Solution
Three tools targeting three content-based attack surfaces: document ingestion → coding assistant context → RAG retrieval optimization. All share the generate → deploy → track methodology with out-of-band callback verification.

---
## Phase 1: Indirect Prompt Injection Detection (v1.0) — IPI

### Scope
- Generate documents with hidden payloads across multiple formats
- 34 hiding techniques across 7 formats (PDF, Image, Markdown, HTML, DOCX, ICS, EML)
- 7 payload styles × 7 payload types (49 template combinations)
- Authenticated callback listener with confidence scoring
- Web dashboard for campaign monitoring
- Deterministic corpus generation for reproducible testing

### Deliverables
- Multi-format payload generator with technique registry
- FastAPI callback server with authenticated endpoints
- SQLite storage with migration support
- CLI: generate, listen, status, techniques, formats, reset
- HTMX web dashboard (campaigns, hits, generate)
- Test harness for payload validation
- Deterministic seed-based generation

### Key Design Decisions
- **Callback-based verification** — proof of execution, not output analysis. This is the core differentiator.
- **Technique diversity over technique depth** — cover many hiding methods across many formats to fingerprint parser behavior, rather than perfecting one technique.
- **Authenticated callbacks** — per-campaign cryptographic tokens eliminate scanner noise. HIGH/MEDIUM/LOW confidence scoring.
- **Dangerous payload gating** — exfil, SSRF, and behavior modification payloads require explicit `--dangerous` flag.

### Phase 1 Research
- 12 confirmed real-world callbacks against Open WebUI
- Parser regression finding: Open WebUI v0.7.2 → v0.8.1 expanded DOCX attack surface
- Multi-model vulnerability matrix: 18 models tested across Ollama, Groq, and OpenRouter
- Key finding: reasoning-capable models use chain-of-thought to organize compliance with malicious instructions, not resist them

### Phase 1 Writeup
**Published:** "When Upgrades Expand the Attack Surface" on richardspicer.io (parser regression, platform abstracted)
**Planned:** "Reasoning Doesn't Protect Against Prompt Injection" — multi-model evidence across providers

---
## Phase 1.5: Coding Assistant Context Poisoning — CXP

### Concept
AI coding assistants treat project-level instruction files as trusted context. These files live in repositories that may be forked, cloned from untrusted sources, or contributed to by external parties. CXP tests whether poisoned instruction files cause coding assistants to produce vulnerable code, exfiltrate data, or execute commands.

### Target Files
- `CLAUDE.md` — Claude Code
- `AGENTS.md` — Multi-assistant convention
- `.cursorrules` — Cursor
- `copilot-instructions.md` — GitHub Copilot
- `.windsurfrules` — Windsurf
- `.gemini/settings.json` — Gemini

### Core Capabilities
- Generate poisoned context file corpora organized by objective (backdoor insertion, credential exfil, dependency confusion, permission escalation) and by assistant format
- Test against real coding assistants with headless interaction and output capture
- Produce behavioral test results: which payloads caused which assistants to produce vulnerable code
- Generate assistant comparison matrix: success rates across Claude Code, Cursor, Copilot, Codex, Windsurf
- Package bounty-ready PoCs: minimal reproduction packages (poisoned repo + trigger prompt + evidence capture)

### Why This Matters
- Completely unoccupied niche — academic research (arxiv 2601.17548v1) catalogs 42 attack techniques but no packaged testing tool exists
- The AGENTS.md consolidation trend means one poisoned file can affect multiple AI coding tools simultaneously
- Every coding assistant with a bug bounty or VDP is a target
- Low implementation complexity — payload generation + headless assistant interaction + output capture

### Deliverables
- Poisoned context file corpus by objective and assistant format
- Behavioral test results (JSON) with exact prompts and outputs
- Assistant comparison matrix with success rates
- Bounty-ready PoC packages

### Phase 1.5 Writeup
**Title:** "Poisoning the Instructions: How Context Files Compromise AI Coding Assistants"
**Target:** Bounty submissions + richardspicer.io

---
## Phase 2.5: RAG Retrieval Poisoning Optimizer — RXP

### Concept
IPI tests whether injected content triggers when retrieved. It works well for controlled knowledge base testing where retrieval is guaranteed by the test setup. RXP (codename Drongo) extends this to contested retrieval scenarios — where poisoned content sits alongside legitimate documents and must win the vector similarity battle to reach the LLM's context window. Named after the fork-tailed drongo — an African bird that mimics alarm calls to manipulate other species into abandoning their food — the tool manipulates retrieval trust signals so poisoned content gets served as legitimate.

### Core Capabilities
- Given a target query domain (e.g., "HR policy," "quarterly report"), generate text optimized for high cosine similarity with likely user queries across common embedding models
- Wrap optimized text + injection payload into document formats (PDF, DOCX, TXT, HTML)
- Validate retrieval rank against test vector DB (ChromaDB)
- Report retrieval success rates across embedding models
- Generate embedding space similarity heatmaps

### Integration with IPI
Natural pairing forming the full RAG attack chain:
1. RXP generates retrieval-optimized text for the target domain
2. IPI wraps it with callback payloads using chosen hiding techniques
3. Combined documents test whether the RAG system retrieves AND executes

RXP and IPI are sibling modules in the countersignal monorepo with shared core infrastructure.

### Deliverables
- Retrieval-optimized poison documents
- Embedding space similarity heatmaps
- Top-k hijack PoCs with retrieval rank evidence
- Retrieval success rate reports across embedding models

### Phase 2.5 Writeup
**Title:** "Winning the Retrieval Battle: Adversarial Document Optimization for RAG Poisoning"
**Target:** richardspicer.io + conference submission

---
## Pre-Release Security Review (before each tool release)

### Static Analysis (SAST)
- `bandit` — Python security linter
- `semgrep` — custom rules for project patterns
- Run in CI on every PR

### CI Testing Matrix
- Cross-platform: `ubuntu-latest` + `windows-latest`
- Python versions: `["3.11", "3.13", "3.14"]` — floor, near-ceiling, and forward-compatibility
- `requires-python = ">=3.11"` means the floor must always be tested

### Dependency Scanning
- `pip-audit` — check against PyPI advisory database
- GitHub Dependabot for ongoing monitoring

### Manual Review Focus
| Area | Check |
|------|-------|
| Path operations | Output paths constrained, no traversal |
| URL validation | Target URLs validated, blocking where appropriate |
| Input handling | All user inputs sanitized |
| Error handling | No sensitive data in error messages |

### Exit Criteria
- Zero high/critical findings from SAST
- No known CVEs in dependencies
- SECURITY.md documents trust boundaries and limitations

---
## Cross-Phase: Ongoing Activities

### Vulnerability Research & Disclosure
- Continuously test AI agent platforms with generated payloads
- Multi-platform testing strengthens research narratives over single-vendor findings
- Responsible disclosure pipeline — document, report, wait for fix, then publish
- Abstract findings to establish patterns across platforms

### Detection Engineering
- Every attack technique that works should produce a detection rule
- Wazuh and Sigma rule generation from observed attack patterns
- Route test traffic through inference-gateway for telemetry capture
- "If I can break it, I should be able to detect it"

### Community & Visibility
- richardspicer.io blog — phase writeups + individual findings
- GitHub — well-documented repos, contribution guides
- Conference submissions — BSides, DEF CON AI Village
- LinkedIn — quality posts on key findings

### Framework Mapping

| Framework | Usage |
|-----------|-------|
| OWASP Top 10 for LLM Applications 2025 | Primary vulnerability taxonomy |
| OWASP Top 10 for Agentic AI | Attack pattern classification |
| MITRE ATLAS | Adversarial ML technique mapping |
| NIST AI RMF | Risk management context |

---
## Success Metrics

### Phase 1 Success (IPI)
- ✅ 34 techniques across 7 formats with E2E testing
- ✅ 12 confirmed real-world callbacks
- ✅ Multi-model, multi-provider testing (18 models)
- ✅ Published finding: parser regression
- ✅ Pre-release security review complete (bandit, semgrep, pip-audit, manual review, dynamic testing)
- Pending: multi-platform testing

### Phase 1.5 Success (CXP)
- Poisoned context files cause at least one major coding assistant to produce vulnerable code
- Comparison matrix covers 3+ assistants
- At least one bounty submission from findings
- Detection rules for context file poisoning patterns

### Phase 2.5 Success (RXP)
- Generated documents achieve top-3 retrieval rank against target queries
- Combined RXP + IPI pipeline produces confirmed callbacks
- Retrieval success validated across 3+ embedding models

### Portfolio Success
- CVE or bounty with name attached
- Tools that other security researchers actually use
- Conference talk accepted
- Blog posts that teach something learned the hard way

---
## Build Sequence

```
countersignal (monorepo)
├── core/     Shared callback infrastructure
├── ipi/      Phase 1 — indirect prompt injection detection
│             └── v0.1.0 released, multi-platform testing ongoing
├── cxp/      Phase 1.5 — coding assistant context poisoning
│             └── Migrated, bounty testing in progress
└── rxp/      Phase 2.5 — RAG retrieval optimization (planned)
              └── IPI companion, completes the RAG attack chain
```

---
## Reference Links
- OWASP Top 10 for LLM Applications 2025: https://owasp.org/www-project-top-10-for-large-language-model-applications/
- OWASP Top 10 for Agentic AI: https://genai.owasp.org/
- MITRE ATLAS: https://atlas.mitre.org/
- Garak: https://github.com/NVIDIA/garak
- PyRIT: https://github.com/Azure/PyRIT
- Spikee: https://github.com/WithSecureLabs/spikee
- Coding Assistant Attack Taxonomy: https://arxiv.org/abs/2601.17548
