# Ask My Notes

Ask My Notes is a local command-line document-search application. It is intentionally small: the first milestone uses only Python's standard library for ingestion, chunking, and keyword retrieval. It is a learning project that will eventually grow into a RAG assistant.

## Contents

- [Project structure](#project-structure)
- [Install](#install)
- [Run a search](#run-a-search)
- [How retrieval works](#how-retrieval-works)
- [Run tests](#run-tests)
- [Next extension points](#next-extension-points)
- [Follow-up exercise](#follow-up-exercise)

## Project structure

```text
documents/       Sample Markdown and text notes
src/
	chunker.py     Split documents into overlapping word chunks
	cli.py         Command-line interface
	loader.py      Recursively load .md and .txt files
	models.py      Typed data objects and the Retriever interface
	search.py      Explainable keyword ranking
tests/           Automated tests for each core component
pyproject.toml   Packaging and test configuration
```

The `Retriever` interface is the extension point for later embedding-based and hybrid implementations. `DocumentChunk` already keeps the source filename and chunk number so future answers can cite passages.

## Install

Python 3.10 or newer is required. Create a virtual environment and install the project with its development dependency:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

The application itself has no runtime dependencies outside the Python standard library.

## Run a search

Put `.txt` or `.md` files anywhere under `documents/`. The loader searches recursively. Then run:

```bash
python -m src.cli search "How does retrieval work?"
```

The command prints up to three ranked passages, each with a score, source filename, and chunk number. Useful options include `--limit`, `--chunk-size`, `--overlap`, `--documents`, and `--verbose`. For example:

```bash
python -m src.cli --documents my-notes --chunk-size 80 --overlap 15 search "testing Python"
```

## How retrieval works

1. The loader finds `.md` and `.txt` files recursively and records each path relative to the documents directory.
2. The chunker splits each file into word windows. With a chunk size of 120 and overlap of 20, the next window starts 100 words later, preserving context at boundaries.
3. The keyword retriever lowercases text and extracts alphanumeric terms. For each chunk, it adds the inverse-document-frequency-weighted count of query terms, limits repeated terms to avoid domination by one word, and normalizes by chunk length.
4. Results are sorted by descending score and ties are made deterministic with source filename and chunk number.

This is keyword search, not semantic search: “retrieval” and “finding” are different terms. That limitation is useful for this milestone because every ranking decision is visible in `src/search.py`.

## Run tests

```bash
python -m pytest
```

## Next extension points

The current boundaries leave room for Sentence Transformer embeddings, cosine similarity, hybrid scoring, PDF-specific loaders, answer generation with citations, retrieval evaluation, and a FastAPI adapter without putting those concerns into the CLI.

## Follow-up exercise

Add a small stop-word filter to `src/search.py` for very common words such as `the`, `is`, and `how`. Add a test showing that a query made only of stop words returns no results, then compare the ranking before and after the change.