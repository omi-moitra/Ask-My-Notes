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

Ask My Notes is a learning project for building a local document-search application before adding the complexity of a full retrieval-augmented generation assistant. The first milestone focuses on understanding the mechanics of ingestion, chunking, metadata, ranking, and command-line interaction.

## What was built

- A typed Python package under `src/`.
- Recursive loading of non-empty `.txt` and `.md` files from `documents/`.
- Configurable word-based chunks with overlap.
- Source filename and one-based chunk number metadata.
- A standard-library keyword retriever with a transparent TF-IDF-inspired score.
- A CLI command that prints up to three ranked passages.
- Sample notes for immediate experimentation.
- Pytest coverage for loading, chunking, validation, ranking, limits, and empty queries.
- Packaging configuration in `pyproject.toml`.
- README usage documentation, educational source comments, and this overview.

## End-to-end flow

1. `src.cli` parses the search query and configuration.
2. `src.loader` walks the document directory and creates `Document` objects.
3. `src.chunker` converts each document into overlapping `DocumentChunk` objects.
4. `src.search.KeywordRetriever` tokenizes chunks, calculates inverse document frequency, and scores query-term matches.
5. The CLI prints sorted `SearchResult` objects with score and citation-friendly metadata.

The components are deliberately separate so each one can be studied and tested independently.

## Important decisions

The implementation uses only the standard library at runtime. This keeps the algorithm visible and avoids hiding the learning goals behind LangChain or LlamaIndex. Word-based chunking is used because it is simple to inspect, and overlap preserves nearby context at chunk boundaries. Keyword matching is literal, so the current system does not infer synonyms or stem words.

The `Retriever` interface is the main extension boundary. Future implementations can add embeddings, cosine similarity, or hybrid scoring while keeping document loading and the CLI contract stable. The current `DocumentChunk` metadata also gives future answer generation enough information to cite sources.

All decisions and their rationale are maintained in [Decisions.md](Decisions.md), under the `initialization` section.

## Validation

The completed suite contains five passing tests:

```text
5 passed
```

The command below was also run successfully against the sample documents:

```bash
.venv/bin/python -m src.cli search "How does retrieval work?"
```

Workspace diagnostics reported no errors.

## Future extension points

The project is ready for later, separate milestones involving Sentence Transformer embeddings, cosine similarity, hybrid retrieval, PDF ingestion, LLM-generated answers with citations, retrieval evaluation, and a FastAPI interface. None of those features are implemented yet.

## How to use it

From the project root:

```bash
source .venv/bin/activate
python -m src.cli search "How does retrieval work?"
python -m pytest
```
