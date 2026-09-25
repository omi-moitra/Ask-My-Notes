# Decisions

## Contents

- [initialization](#initialization)
- [Stop-word filtering](#stop-word-filtering)
- [Semantic search](#semantic-search)
- [Hybrid search](#hybrid-search)
- [Local grounded answers](#local-grounded-answers)

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

## Stop-word filtering

Implemented on 2026-09-22 according to [the feature spec](ai/stop-word-filter-spec.md).

- **Vocabulary:** Use the exact 26-word specification vocabulary in an immutable `STOP_WORDS` set. Keep negation and numbers; this deliberately small list is inspectable and introduces no dependency or configuration surface.
- **Shared filtering:** Filter exact normalized tokens in `tokenize` for both queries and passages. Preserve token order and repetitions, and retain original chunk text and metadata for display.
- **Normalization:** Calculate counts, term frequencies, and passage-length normalization from retained tokens so extra stop words cannot dilute relevance. Keep the existing scoring formula, repetition cap, query deduplication, limits, and tie-breakers.
- **Empty chunks:** Include all original chunks in the IDF corpus size. Skip chunks with no matching terms before division, ensuring empty retained-token counts are safe. Stop-word-only queries reuse the existing no-results path.
- **Limitations:** The fixed English list can remove meaningful words in titles or phrases. There is no override, and retaining negation does not provide semantic understanding.
- **Documentation:** Every file changed for this feature has an updated contents section and explanatory comments or prose describing the behavior and rationale.
- **Validation:** All 9 tests pass. Both required CLI smoke checks exit successfully. The controlled comparison removes `filler.txt` (previously first at 3.442672), leaving `retrieval.md` first at 0.702733. Actual results and reproduction instructions are in the README.


## Semantic search

Implemented against [the semantic feature spec](ai/semantic-search-spec.md). Historical validation counts above describe earlier milestones; current results are in [the semantic validation report](ai/semantic-search-results.md).

- **Optional mode:** Keep keyword as the default and preserve its dependency-free runtime. Add `--retriever semantic`, with semantic-only cache/offline options validated by argparse.
- **Model:** Use CPU `sentence-transformers/all-MiniLM-L6-v2` at revision `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`. Pin Sentence Transformers 5.1.2; record transitive versions tested on Python 3.14.3 rather than claiming untested interpreter coverage.
- **Lifecycle:** Delay optional imports/model loading until actual encoding. Snapshot nonblank chunks into a tuple, validate and cache their vectors once per instance, and rebuild passage vectors on each CLI invocation.
- **Scoring:** Normalize vectors and use their dot product as cosine. Reject malformed/nonfinite/zero vectors. Sort full scores with source/chunk ties, retaining negative scores without a fabricated relevance threshold.
- **Text policy:** Embed original text, including stop words. Warn when model-token counts exceed the sequence limit; preserve original text for display. Word-based chunking stays unchanged.
- **Offline loading:** Resolve the pinned local snapshot first and pass its local path to the model, avoiding remote optional-file probes. Tests prohibit DNS and socket connections and check both complete and empty caches.
- **Failure handling:** Translate expected semantic dependency/model/output failures into actionable CLI errors with exit 1. Invalid option combinations exit 2; no silent keyword fallback occurs.
- **Evidence:** All 39 deterministic tests and 3 network-blocked real-model tests pass. Both predefined paraphrases recovered their expected passage first; both exact matches also ranked first. Unrelated questions still produced neighbors.
- **Education:** Extend the concepts walkthrough and Python tutorial with cosine arithmetic, lazy optional dependencies, encoder test doubles, cache behavior, and limits. Keep companion slides, narration, TOCs, and source excerpts synchronized.


## Hybrid search

Implemented on 2026-09-23 against [the hybrid spec](ai/hybrid-search-spec.md). Earlier counts above describe historical milestones; [current validation](ai/hybrid-search-results.md) records 60 deterministic and 5 offline integration checks.

- **Composition:** Keep both branch algorithms unchanged, reuse their instances, and pass them the same unique nonblank snapshot. Keyword gets a private list; semantic remains lazy. Caller mutations cannot realign passages with stale vectors/counts.
- **Fusion:** Equal weights, constant 60, one-based positions, and full eligible-corpus branch limits. Do not add raw scores or truncate candidates to the display limit. Deterministic output uses source and chunk number for exact ties.
- **Identity:** Deduplicate `(source, chunk_number)`, preserving first original text; conflicting text raises ValueError. The helper counts repeated branch entries once at their first supplied position without renumbering later results.
- **Failure policy:** Semantic errors abort hybrid search without partial fallback. Model/cache options apply to semantic and hybrid; keyword remains dependency-free and the default.
- **Evaluation integrity:** Preserve all 23 original evidence labels and historical results.json. Store new rankings, corpus hashes, component ranks, and versions in separate hybrid artifacts. The runner no longer overwrites the historical report.
- **Observed tradeoff:** Hybrid Hit@3 is 75%, below semantic's 85% and equal to keyword's 75%. Relative to semantic it gains one answer and loses three; no labels or constants were tuned to conceal this. Full semantic rankings give every literal match a second vote, even when weak.
- **Education:** Explain RRF arithmetic, snapshots, dictionaries/sets, one-based enumerate, full candidates, and a controlled ranking regression. Keep guides, scripts, slides, TOCs, and embedded source excerpts consistent.

## Local grounded answers

- **User direction:** Local generation avoids per-request hosted API fees. Hosted switching is separately specified and not implemented.
- **Hardware and model:** An 8 GiB Apple M1 with limited disk space uses Ollama 0.34.3 and pinned Qwen2.5 1.5B Q4_K_M (approximately 986 MB). Larger weights were not downloaded. Model assets/runtime stay in ignored caches.
- **Boundaries:** `answering.py` owns bounded context, immutable answer records, strict validation, and rendering. `local_generator.py` owns fixed-loopback transport and local model checks. `search` stays unchanged; `ask` defaults to semantic evidence.
- **Offline behavior:** Explicit setup downloads assets; answering never pulls, redirects, uses cloud aliases, or falls back. OS-level loopback-only sandbox validation covers Ollama and its children, in addition to client network checks. The daemon must be started separately; no background service was installed.
- **Resource policy:** One generation request, finite deadline, 512-token output, whole-passage budget, conservative context bound, and immediate model unload. Small models save resources but do not guarantee good answers.
- **Quality evidence:** Fixed synthetic questions expose over-abstention near an injected instruction and incomplete handling of conflicting notes. General prompt clarification was tested without changing labels. Document actual final outcomes and the remaining failed generation check; do not weaken it to make the suite green. Structural correctness and source support are separate measurements.
- **Teaching:** Explain the two local models, injected generators, JSON schema versus factual support, budgets, citations, and runtime setup in all six learning companions. See [RAG validation](ai/rag-answer-results.md).
