# Decisions

## Contents

- [initialization](#initialization)

## initialization

- **Project scope:** Build the first milestone as a local command-line document-search application, without implementing embeddings, an LLM, PDFs, FastAPI, or evaluation workflows yet.
- **Existing repository:** The workspace initially contained only a title-only `README.md` and `.gitignore`, so there was no existing application design or public API to preserve.
- **Python version:** Target Python 3.10 or newer through `pyproject.toml`.
- **Dependencies:** Keep runtime dependencies empty and use the Python standard library for loading, chunking, tokenization, scoring, logging, and the CLI. Use `pytest` only as a development dependency.
- **Project structure:** Separate loading, chunking, shared models, search, and CLI code into `src/loader.py`, `src/chunker.py`, `src/models.py`, `src/search.py`, and `src/cli.py`.
- **Data model:** Represent source files with `Document`, searchable sections with `DocumentChunk`, and ranked matches with `SearchResult` dataclasses.
- **Extension boundary:** Define a small `Retriever` interface with `search(query, limit)` so embedding, semantic, and hybrid retrievers can be added without coupling them to ingestion or the CLI.
- **File support:** Recursively load only `.txt` and `.md` files from the configured documents directory. Store each source path relative to that directory for portable citations.
- **Chunking:** Use readable word-based windows with configurable `chunk_size` and `overlap`. Preserve the source filename and one-based chunk number on every chunk.
- **Keyword ranking:** Use lowercase alphanumeric tokenization and a transparent TF-IDF-inspired score. Weight rarer terms with inverse document frequency, cap repeated-term counts at three, and normalize by chunk length.
- **Result ordering:** Return at most three results by default, sorted by descending score with source filename and chunk number as deterministic tie-breakers.
- **CLI shape:** Support the requested command `python -m src.cli search "..."`, plus options for document directory, chunk size, overlap, result limit, and verbose logging.
- **Sample data:** Add one Markdown retrieval note and one text note so a fresh checkout can be searched immediately.
- **Documentation:** Expand `README.md` with structure, installation, usage, algorithm explanation, extension points, testing instructions, and a small follow-up exercise.
- **Testing:** Add focused tests for recursive file loading, metadata-preserving overlapping chunks, invalid chunk settings, keyword ranking, result limits, and empty queries.
- **Environment finding:** The shell's `python3` path differed from the VS Code-configured Python environment. VS Code reported `pytest` installed in the configured environment, so final tests should use the interpreter path that actually contains it.
- **Keyword behavior clarification:** Keep token matching literal in this milestone; the retriever does not stem words, so `document` and `documents` are distinct terms.
- **Validation outcome:** Workspace diagnostics report no errors. The CLI smoke test completed and returned a ranked retrieval passage. The full test suite passes in `.venv` with 5 tests passing.
- **Documentation update:** Add educational comments and contents sections to the project files, and create `PROJECT_OVERVIEW.md` to explain the completed work and its rationale.
- **Documentation convention:** Python files use module-level contents docstrings plus comments around meaningful control-flow steps; Markdown and text files use navigable contents sections; configuration files use contents comments.
- **Overview document:** Use `PROJECT_OVERVIEW.md` for the milestone narrative so `README.md` can remain focused on setup and day-to-day usage.
- **Final validation:** After the documentation pass, `.venv/bin/pytest -q` reports 5 passing tests, diagnostics report no errors, and the CLI smoke test still succeeds.