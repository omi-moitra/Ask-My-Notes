# Ask My Notes: Project Overview

## Contents

- [Purpose](#purpose)
- [What was built](#what-was-built)
- [End-to-end flow](#end-to-end-flow)
- [Important decisions](#important-decisions)
- [Validation](#validation)
- [Future extension points](#future-extension-points)
- [How to use it](#how-to-use-it)

## Purpose

Ask My Notes is a learning project for building a local document-search application with an initial local retrieval-augmented generation workflow. The first milestone focuses on understanding the mechanics of ingestion, chunking, metadata, ranking, and command-line interaction.

## What was built

- A typed Python package under `src/`.
- Recursive loading of non-empty `.txt` and `.md` files from `documents/`.
- Configurable word-based chunks with overlap.
- Source filename and one-based chunk number metadata.
- A standard-library keyword retriever with a transparent TF-IDF-inspired score.
- A shared stop-word filter for indexed passages and queries, with original text preserved.
- Optional CPU semantic retrieval with pinned local embeddings, cosine ranking, lazy loading, and offline model-cache support.
- Opt-in hybrid retrieval using full-corpus reciprocal-rank fusion, sharing existing keyword/model branches.
- A `search` command that prints ranked passages.
- An `ask` command that uses a local Qwen model through Ollama, validates citations, and shows supporting evidence.
- Sample notes for immediate experimentation.
- Pytest coverage for loading, chunking, validation, ranking, limits, and empty queries.
- Packaging configuration in `pyproject.toml`.
- README usage documentation, educational source comments, and this overview.

## End-to-end flow

1. `src.cli` parses the search query and configuration.
2. `src.loader` walks the document directory and creates `Document` objects.
3. `src.chunker` converts each document into overlapping `DocumentChunk` objects.
4. The CLI selects `KeywordRetriever` by default, or `SemanticRetriever` or `HybridRetriever` explicitly. Keyword mode uses filtered token counts; semantic mode embeds original text and ranks by cosine similarity.
5. The CLI prints sorted `SearchResult` objects with score and citation-friendly metadata.

The components are deliberately separate so each one can be studied and tested independently.

## Important decisions

The base keyword implementation uses only the standard library at runtime; the optional semantic extra loads its model stack only when needed. This keeps the algorithm visible and avoids hiding the learning goals behind LangChain or LlamaIndex. Word-based chunking is used because it is simple to inspect, and overlap preserves nearby context at chunk boundaries. Keyword matching is literal, while the optional semantic model can recover some paraphrases without shared terms.

The `Retriever` interface is the main extension boundary. All three implementations share the result contract; future implementations can add reranking while keeping document loading and the CLI contract stable. The current `DocumentChunk` metadata supports request-local citations in generated answers. `Generator` is a separate injectable boundary; its adapter uses local Ollama without hosted calls.

All decisions and their rationale are maintained in [Decisions.md](Decisions.md), under the `initialization`, `Stop-word filtering`, `Semantic search`, and `Hybrid search` sections.

## Validation

Local RAG validation on 2026-09-25: 122 deterministic checks and five offline embedding checks pass. Real local generation runs inside an external-network-blocked daemon; the small model still has a documented generation-quality failure. See [the RAG report](ai/rag-answer-results.md), [answer evaluation](evaluations/local-answer-results.md), and [README setup](README.md#local-model-setup). The following retrieval measurements are the preserved earlier baseline.

Validation on 2026-09-23: **60 deterministic tests pass** in both keyword-only and model-enabled environments, and **5 explicit offline integration tests pass** with socket/DNS calls prohibited. The unchanged six-query fixture preserves the standalone acceptance checks; hybrid moves its paraphrase answers from semantic rank one to ranks three and two.

The existing 23-question evaluation now measures all three modes against identical chunks and unchanged evidence labels: keyword Hit@1/Hit@3 75%/75%, semantic 80%/85%, hybrid 75%/75%. Hybrid recovers one semantic miss and regresses on three semantic hits; it remains opt-in. All methods return passages for the three unrelated queries. Historical results are preserved.

See [the current validation report](ai/hybrid-search-results.md) for setup and limitations, and [the detailed evaluation](evaluations/hybrid-results.md) for per-query results, component ranks, and corpus hashes.

## Future extension points

The project is ready for later, separate milestones involving reranking, PDF ingestion, optional hosted generation, broader answer evaluation, and a FastAPI interface. Local generated answers and diagnostic evaluations are implemented.

## How to use it

After local model setup: `.venv-semantic/bin/python -m src.cli ask "How does retrieval work?" --retrieval-offline`. Use `--retriever keyword` in the base environment. `search` retains its earlier behavior.

From the project root:

```bash
source .venv/bin/activate
python -m src.cli search "How does retrieval work?"
python -m pytest
```
