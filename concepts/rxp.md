# RXP

> RAG retrieval poisoning optimizer — guarantee your payloads get retrieved.

## Purpose

IPI-Canary tests whether injected content triggers agent action when it reaches the LLM's context window. It assumes the payload is already retrieved. Drongo solves the prerequisite: how to guarantee that poisoned content wins the vector similarity battle and actually gets retrieved into context. Named after the fork-tailed drongo — an African bird that mimics alarm calls to manipulate other species' behavior and steal their food — the tool manipulates the trust signals of vector retrieval systems so poisoned content gets served up as legitimate. No existing tool optimizes text specifically to hijack the embedding space for adversarial retrieval. Drongo is the missing first half of the RAG attack chain — without it, IPI-Canary testing against RAG systems relies on luck rather than engineering.

## Program Context

Phase 2.5 in the CounterSignal program. Sits between IPI-Canary (which handles payload wrapping and callback tracking) and the target RAG system. The natural integration:

1. Drongo generates retrieval-optimized text for a target query domain
2. IPI-Canary wraps it with callback payloads using chosen hiding techniques
3. Combined documents test whether the RAG system retrieves AND executes

Implemented as the rxp module within the countersignal monorepo.

## Core Capabilities

- Given a target query domain (e.g., "HR policy," "quarterly report"), generate text optimized for high cosine similarity with likely user queries across common embedding models.
- Support multiple embedding models for cross-model testing (sentence-transformers, OpenAI embeddings, Cohere, etc.).
- Wrap optimized text + injection payload into document formats compatible with IPI-Canary (PDF, DOCX, TXT, HTML).
- Validate retrieval rank against a test vector database — confirm the poisoned document achieves top-k retrieval for target queries.
- Report retrieval success rates across embedding models with statistical confidence.
- Generate embedding space similarity heatmaps for research visualization.

## Key Design Decisions

- **Retrieval optimization is the core, not payload generation.** IPI-Canary handles payloads. Drongo handles ensuring those payloads reach the context window. Clear scope boundary.
- **ChromaDB as the test vector database.** Lightweight, embeddable, Python-native. Good enough for validation without requiring infrastructure. Production RAG systems use various backends, but retrieval rank testing only needs a reference implementation.
- **Multi-model testing is required.** Different RAG systems use different embedding models. Text optimized for `all-MiniLM-L6-v2` may not rank well against `text-embedding-3-small`. The tool must test across models, not assume one.
- **Adversarial text must remain plausible.** Pure embedding-space optimization can produce gibberish that ranks well but gets filtered by preprocessing. Generated text must read as legitimate content — a document that a human or automated filter wouldn't reject.
- **Output format must be compatible with IPI-Canary's input.** The integration path is Drongo output → IPI-Canary generator input. Define a shared interface (file or data model) before building.
- **Cross-platform** — must run on Windows, macOS, and Linux. No platform-specific shell commands in source or test fixtures.

## Open Questions

- **Module or repo?** Standalone repo (`richardspicer/Drongo`) gives more research visibility and independent release cycle. Module within IPI-Canary gives tighter integration and simpler user workflow. Key question: does Drongo have standalone research value beyond IPI-Canary? If researchers would use it independently to study retrieval poisoning (without needing callback tracking), standalone is justified.
- **Optimization approach:** Gradient-based optimization against embedding models (more precise but requires model access and compute), evolutionary/heuristic text generation (less precise but works without gradients), or LLM-assisted generation with similarity feedback loops (practical but less rigorous)? The choice significantly affects compute requirements and effectiveness.
- **Target query generation:** How to generate realistic user queries for a given domain? LLM-generated query sets? Sampled from search logs? Synthetic corpus? The quality of target queries determines whether retrieval optimization generalizes to real-world use.
- **Chunk-level vs. document-level optimization:** RAG systems chunk documents before embedding. Should Drongo optimize at the chunk level (more precise) or document level (simpler)? Chunk-level requires understanding the target system's chunking strategy.
- **Evaluation metric:** Top-1 retrieval rank? Top-k presence? Cosine similarity delta vs. legitimate documents? Need a clear metric that translates to "the poisoned document will be retrieved" across different RAG configurations.

## Artifacts

- Retrieval-optimized poison documents (text files or wrapped in IPI-Canary-compatible formats).
- Retrieval rank reports: per-document, per-query, per-embedding-model results.
- Embedding space similarity heatmaps for research visualization.
- Top-k hijack PoCs with retrieval rank evidence — "this document displaced the legitimate HR policy for 9 out of 10 test queries."
- Cross-model comparison matrices: which embedding models are most susceptible to retrieval poisoning.

## Relation to Other Tools

- **IPI-Canary** handles payload generation and callback tracking. Drongo handles retrieval optimization. Together they test the full RAG attack chain: retrieve → inject → execute → callback. Drongo does NOT generate callback payloads or track execution.
- **CXP-Canary** targets coding assistant context files, not RAG retrieval. No interaction.
- **agent-chain** (CounterAgent Phase 3) may incorporate RAG poisoning as a step in broader attack chains. Drongo provides the retrieval optimization primitive; agent-chain composes it with other attack steps.
- **Garak / PyRIT** focus on LLM-level testing. Drongo operates at the retrieval layer — it doesn't care what the LLM does with retrieved content, only whether the content gets retrieved.

---

*This is a concept doc, not an architecture doc. It captures intent and constraints. The full Architecture doc gets written when development begins.*
