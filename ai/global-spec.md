# Ask My Notes: Global AI Specification

Status: Project-wide context and direction  
Last reviewed: 2026-09-25  
Scope: This repository, for AI-assisted development and human contributors.

## Contents

- [Purpose](#purpose)
- [Current state](#current-state)
- [Architecture](#architecture)
- [Design principles](#design-principles)
- [Direction and roadmap](#direction-and-roadmap)
- [Evaluation](#evaluation)
- [Development guidance](#development-guidance)
- [References and maintenance](#references-and-maintenance)

## Purpose

Ask My Notes is a local Python command-line application for finding useful passages in personal Markdown and text notes. It is also a learning project: its implementation, tests, explanations, and teaching materials should make retrieval understandable to someone learning Python and AI systems.

The intended direction is a retrieval-augmented generation (RAG) assistant that answers questions using evidence from the user's notes and cites supporting passages. The project builds toward that outcome incrementally: understand ingestion and retrieval first, compare retrieval strategies, and later add grounded answer generation. Today `search` returns passages and `ask` generates local answers with citations; small-model answer quality has documented limitations.

The primary workflow is to place notes in a local directory, ask a question through the CLI, and inspect ranked passages with source paths and chunk numbers. The learning workflow is to trace those results through small modules, tests, and companion explanations.

This specification records the existing direction. Future possibilities are not commitments to implement every feature, and this document does not expand an individual task beyond the user's requested scope.

## Current state

| Capability | Status | Behavior |
| --- | --- | --- |
| Ingestion | Implemented | Recursively loads non-empty `.md` and `.txt` files. |
| Chunking | Implemented | Overlapping word windows; defaults are 120 words with 20 words of overlap. |
| Keyword retrieval | Implemented; default | Literal normalized tokens, a fixed stop-word filter, and transparent TF-IDF-inspired ranking. |
| Semantic retrieval | Implemented; opt-in | Local CPU embeddings, cosine ranking, lazy model loading, and offline cache support. |
| Evaluation | Implemented | A fixed 23-question keyword/semantic/hybrid comparison and a separate six-query semantic integration fixture. |
| Hybrid retrieval | Implemented; opt-in | Combines full keyword and semantic rankings with reciprocal rank fusion. |
| Generated answers | Implemented with a known model-quality failure | Local Ollama/Qwen answers with validated citations; see the RAG results report. |
| PDFs, API or web UI | Future possibilities | No implementation or fixed delivery sequence is established. |

Python 3.10 or newer is required. The base keyword application has no runtime dependencies outside the standard library. Semantic mode uses the optional `sentence-transformers==5.1.2` dependency and CPU model `sentence-transformers/all-MiniLM-L6-v2`, pinned to revision `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`.

Model assets default to `.cache/ask-my-notes/models`. Online mode may download assets or check the network; a warm cache alone does not guarantee offline operation. Explicit offline mode requires complete cached assets and avoids network access. Notes are encoded locally. Passage vectors are reused within a retriever instance and rebuilt on each CLI invocation; there is no persistent passage index.

Known limits are part of the product description. Keyword search does not stem words or understand paraphrases. Semantic search returns nearest neighbors even for unrelated questions and negative similarities, with no relevance threshold. Scores are not confidence probabilities. Model token limits can truncate an input even when the displayed passage is longer; warnings expose that limitation. Neither method establishes that a returned passage answers the question.

## Architecture

```text
CLI configuration + local files
    -> loader -> Document objects
    -> chunker -> DocumentChunk objects
    -> selected Retriever -> SearchResult objects
    -> CLI display with passage text and source metadata
```

| Location | Responsibility |
| --- | --- |
| `src/loader.py` | File discovery, text loading, and source paths relative to the collection. |
| `src/chunker.py` | Word windows, overlap, and one-based chunk numbering. |
| `src/models.py` | Shared `Document`, `DocumentChunk`, `SearchResult`, and `Retriever` contracts. |
| `src/search.py` | Keyword tokenization, stop-word filtering, indexing, and ranking. |
| `src/semantic.py` | Encoder boundary, optional model/cache lifecycle, vector validation, and cosine ranking. |
| `src/cli.py` | Arguments, component wiring, expected error handling, and display. |
| `tests/` | Deterministic behavior checks and explicitly selected real-model checks. |
| `evaluations/` | Labeled questions, evaluation runner, and recorded results. |

`Retriever.search(query, limit=3)` returns a list of `SearchResult` objects. Each result pairs a score with a `DocumentChunk`, retaining passage text, relative source path, and one-based chunk number. Preserve this boundary when adding retrieval methods so ingestion and rendering remain independent of ranking algorithms.

Sort using full-precision scores, then source path and chunk number for deterministic ties. Blank queries and nonpositive limits return no results; semantic mode avoids model loading for these requests and empty eligible corpora. Keyword and cosine scores have different meanings and must not be added or compared as though they share a scale.

Keep keyword as the default. Global CLI options precede `search`; query options follow it. Completed searches, including no matches, exit 0. No loaded documents and expected semantic dependency/model failures exit 1. Argument usage errors exit 2. Semantic failures produce guidance rather than silently switching to keyword results. Preserve existing behavior unless a scoped feature explicitly changes it.

## Design principles

1. **Teach through inspectable code.** Prefer small typed modules and explicit algorithms. Explain consequential choices and edge cases. Avoid hiding the learning goals behind orchestration frameworks.
2. **Keep the base installation small.** Keyword search and default tests must work without model dependencies, cached assets, or network access. Load optional dependencies only when needed.
3. **Keep local processing explicit.** Preserve local note encoding and the distinction between asset setup and offline inference. A future hosted generation service needs a separate design explaining what note content leaves the machine.
4. **Preserve evidence.** Retrieval normalization must not replace displayed passage text. Retain metadata for inspection and future citations.
5. **Measure improvements.** Complexity does not guarantee relevance. Report misses, irrelevant neighbors, and regressions; do not change labels to manufacture a win.
6. **Extend existing boundaries.** Compose retrievers behind the shared interface. Introduce infrastructure only for a demonstrated requirement.

## Direction and roadmap

### Completed foundation

Ingestion, chunking, keyword ranking, stop-word filtering, optional local semantic ranking, and comparative evaluation form the current baseline. Evaluation already exists even though older overview language lists it as a future extension.

### Completed hybrid milestone

The [hybrid implementation](hybrid-search-results.md) uses equal-weight reciprocal rank fusion with constant 60, full branch rankings, stable passage identities, and existing semantic cache handling. It remains opt-in. On the unchanged diagnostic set, hybrid Hit@3 was 75% versus semantic's 85%; correct fusion did not improve aggregate relevance.

### Local grounded-answer milestone

The [RAG answer specification](rag-answer-spec.md) now has a local implementation: `ask` retrieves evidence, generates an answer using Ollama/Qwen2.5 1.5B, validates citation identifiers, and displays original supporting passages. `ask` defaults to semantic retrieval; `search` retains keyword as default. Setup and caches are documented in the README. No hosted API calls are implemented.

The [validation report](rag-answer-results.md) records deterministic checks, external-network isolation, generation checks, and a fixed answer evaluation. The small model has a remaining quality failure; do not equate working code or citation validity with reliable factual support. Reranking and a [hosted adapter](hosted-generation-switch-spec.md) remain separate future choices.

### Longer-term direction

Improve measured answer quality before adding broad new capabilities. Retrieved text is evidence, not instructions that override the assistant's task. Further model/provider support should be separately scoped.

PDF-specific loaders and a FastAPI adapter are documented extension points. They follow the initial answer-generation milestone unless priorities change. Persistent indexes, vector databases, reranking, source diversity, relevance thresholds, and a web interface are not current commitments. Introduce them through concrete feature proposals with a reason and validation plan.

## Evaluation

Use deterministic tests for algorithm contracts and fake encoders for model-independent orchestration. Real-model tests are explicitly selected with the `integration` marker, use cached assets with networking blocked, and fail with setup guidance when requested prerequisites are absent.

The existing evaluation has 20 answerable questions and 3 unrelated questions. A hit requires a labeled evidence phrase in a returned chunk, not merely the correct source file. Report Hit@1 and Hit@3 for answerable questions separately from unrelated questions returning results. The six-query integration fixture is a distinct check; do not conflate the datasets.

The recorded [evaluation report](../evaluations/README.md) shows keyword Hit@1/Hit@3 of 75%/75% and semantic results of 80%/85%; both methods return passages for all three unrelated questions. These are historical results for the recorded corpus, not guarantees or measurements performed for this specification. Full evidence is in [results.json](../evaluations/results.json).

For new comparisons, preserve labels and record corpus hashes, chunk settings, model revision, relevant versions, and commands. Compare methods on the same snapshot and preserve historical artifacts when adding new comparisons. Success means the feature works, contracts remain intact, limits are visible, and another contributor can reproduce and understand the evidence.

## Development guidance

Read relevant source, tests, feature specifications, and decision history before editing. Inspect the working tree and preserve existing user work. A ready feature specification is a plan, not proof that its code exists. Describe discrepancies between implementation and documentation rather than treating planned behavior as implemented.

Use appropriate checks from the repository root:

```bash
# Deterministic tests; no model dependency or network required.
.venv/bin/python -m pytest -q

# Representative keyword CLI check.
.venv/bin/python -m src.cli search "How does retrieval work?"

# Explicit real-model checks; semantic dependencies and cached assets required.
.venv-semantic/bin/python -m pytest -m integration -s -q

# Existing evaluation; writes evaluations/hybrid-results.json and hybrid-results.md.
.venv-semantic/bin/python -m evaluations.run_retrieval
```

These environment names describe this workspace; new checkouts should follow [README installation instructions](../README.md#install). Never report historical test counts as freshly executed validation. Scale verification to the change; documentation-only work does not require downloading or rerunning a model.

Keep README usage, the overview, and the decision log aligned with changed behavior. Feature specs define scope and acceptance; result reports record actual outcomes. Maintain accurate contents sections and explanations appropriate to each edited file's format.

Teaching materials are part of the project: `concept.md`, `concepts-script.md`, `concept-presentation.html`, `python-for-dummies.md`, `python-for-dummies-script.md`, and `python-for-dummies-slideshow.html`. When a feature affects them, synchronize explanations, runnable examples, narration, slide navigation, and source snapshots. Execute examples and record visual verification limitations. Follow the feature spec when it requires a broader teaching update.

## References and maintenance

| Reference | Use |
| --- | --- |
| [README](../README.md) | Installation, commands, and day-to-day behavior. |
| [Project overview](../PROJECT_OVERVIEW.md) | Narrative explanation of implemented milestones. |
| [Decision log](../Decisions.md) | Design rationale and historical outcomes. |
| [Stop-word specification](stop-word-filter-spec.md) | Keyword filtering requirements. |
| [Semantic specification](semantic-search-spec.md) | Local embedding requirements. |
| [Semantic validation](semantic-search-results.md) | Recorded evidence and tested environment. |
| [Hybrid specification](hybrid-search-spec.md) | Requirements for completed hybrid retrieval. |
| [RAG answer specification](rag-answer-spec.md) | Requirements for implemented local answers and outstanding validation. |
| [RAG validation](rag-answer-results.md) | Actual local runtime checks and measured limitations. |
| [Hosted-switch specification](hosted-generation-switch-spec.md) | Future opt-in hosted generation and return to local operation. |
| [Evaluation report](../evaluations/README.md) | Diagnostic comparison and reproduction command. |

Use this document for project-wide orientation and the relevant feature spec for detailed scope. Explicit user instructions govern the task. When implementation, a plan, and historical results disagree, inspect the code and tests and make the discrepancy clear.

Update this specification when a milestone ships, direction changes, or an architectural contract changes. Move completed work out of planned status, link its evidence, and update the review date. Keep speculative work marked and unsettled choices open until a scoped decision is made.
