# Feature Spec: Local Semantic Search

Status: Implemented and verified (2026-09-22)  
Created: 2026-09-22

## Table of contents

- [Purpose](#purpose)
- [Definitions](#definitions)
- [In scope](#in-scope)
- [Out of scope](#out-of-scope)
- [Architecture and model](#architecture-and-model)
- [Search behavior](#search-behavior)
- [CLI and installation](#cli-and-installation)
- [Downloads, caching, and offline use](#downloads-caching-and-offline-use)
- [Testing and comparison](#testing-and-comparison)
- [Documentation and teaching materials](#documentation-and-teaching-materials)
- [Acceptance criteria](#acceptance-criteria)
- [Definition of done](#definition-of-done)
- [Verification](#verification)

## Purpose

Add a local semantic retriever that can rank passages by meaning when a question and a relevant passage use different words. Preserve keyword search as the default and make both approaches easy to compare through the existing CLI.

This follows the completed [stop-word filtering milestone](stop-word-filter-spec.md). It introduces embeddings and cosine similarity as learning concepts. It still returns passages with sources, rather than generating answers. The checked definition of done records the completed implementation; measured evidence is linked below.

## Definitions

- **Embedding:** A numeric vector produced by a model for a passage or query.
- **Semantic retrieval:** Ranking passages by similarity between their embeddings and the query embedding; it can recognize some paraphrases but can also return irrelevant passages.
- **Cosine similarity:** The dot product of two vectors divided by the product of their lengths. For unit-length vectors, it equals their dot product.
- **Model cache:** Downloaded model assets reused between runs.
- **Passage index:** The in-memory association between original chunks and their embeddings. This milestone rebuilds it for each CLI invocation.
- **Offline mode:** Loading cached model assets without attempting network access.

## In scope

- Implement `SemanticRetriever` using the existing `Retriever.search(query, limit)` contract and `SearchResult` dataclass.
- Encode passages and queries locally with one fixed Sentence Transformer model.
- Rank with cosine similarity and preserve source filename, chunk number, and original passage text.
- Add explicit CLI selection between keyword and semantic retrieval.
- Keep semantic dependencies optional so keyword-only installations remain lightweight.
- Support a configurable model-cache directory and explicit offline loading.
- Add deterministic unit tests using a fake encoder, CLI tests, and a separately invoked real-model comparison.
- Update project documentation and both sets of learning materials, with explanatory comments and TOCs.

## Out of scope

- LLM-generated answers, remote embedding APIs, or sending notes to a hosted inference service.
- Hybrid scores, rerankers, vector databases, approximate nearest-neighbor search, or persistent passage indexes.
- PDF ingestion, a web UI, FastAPI, or changes to file loading and chunk boundaries.
- Model fine-tuning, model selection menus, custom model paths, GPU optimization, or multilingual quality guarantees.
- A general evaluation platform, automatic relevance thresholds, or guarantees that semantic search always outperforms keyword search.
- Changes to the completed keyword stop-word policy or its default behavior.

## Architecture and model

Add `src/semantic.py` for the semantic retriever and a small injectable encoder boundary. Tests must be able to supply deterministic embeddings without importing the optional ML stack. Keep CLI orchestration in `src/cli.py`; both retrievers return the existing data objects.

Use `sentence-transformers/all-MiniLM-L6-v2` as the initial CPU model. Its model card describes 384-dimensional embeddings and default truncation beyond 256 word pieces. This is a bounded project choice for learning, not a claim that it is the best available retrieval model. [Model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2).

During implementation, resolve and record an immutable model revision and compatible tested dependency versions. Use that revision for downloads and offline loading; do not leave the final implementation dependent on a moving model branch. Preserve Python 3.10 compatibility or identify a concrete compatibility blocker before changing the project's supported Python version.

The Sentence Transformers API exposes model revision, cache directory, local-only loading, and normalized embeddings. Use these supported controls rather than implementing a download manager. [Official API reference](https://www.sbert.net/docs/package_reference/sentence_transformer/model.html).

Copy the supplied chunk collection into an immutable sequence so subsequent caller mutations cannot misalign passages and embeddings. Encode eligible passages in batches once per retriever instance and reuse their embeddings across queries. Instantiate the model only when a nonempty search actually needs it; empty corpora, blank queries, and nonpositive limits must not trigger downloads or encoding.

## Search behavior

1. Pass original chunk text and query text to the model's own tokenizer. Do not run the keyword tokenizer or remove stop words first: natural-language context is useful to an embedding model.
2. Return `[]` for empty/whitespace-only queries, empty corpora, and nonpositive limits. Skip whitespace-only chunks if supplied directly to the retriever. Preserve all other original chunk metadata.
3. Nonblank punctuation-only and stop-word-only queries use normal semantic encoding. Unlike keyword search, they are not guaranteed to return no results; document this distinction explicitly.
4. Obtain unit-length vectors and score every eligible passage using cosine similarity. Return up to `limit` results, including zero or negative similarities when they fall within the requested top results. Do not add an arbitrary relevance cutoff.
5. Sort by descending raw score, then source filename, then chunk number. Keep full precision for sorting and the existing three-decimal CLI display. Promise deterministic ties for identical input vectors, not bit-for-bit model scores across hardware or library versions.
6. Treat scores as relative similarity, not confidence probabilities. Keyword and semantic scores are on different scales and must not be directly compared or merged.
7. Reject malformed encoder outputs—wrong number of vectors, inconsistent dimensions, nonfinite values, or zero-length vectors—with clear errors before ranking. Do not silently return invalid scores or fall back to keyword search.

Keep existing word-based chunking. A whitespace word count does not guarantee a fit within the model's word-piece limit. Detect overlength query/chunk inputs with the model tokenizer before encoding and emit a concise warning to stderr that truncation occurs; preserve full original text for display. Test the warning with a fake tokenizer, and document that the unseen tail cannot contribute to similarity. Token-aware rechunking is outside this milestone.

## CLI and installation

Implemented commands:

```bash
# The base installation and existing search behavior remain available.
python -m pip install -e '.[dev]'
python -m src.cli search "How does retrieval work?"

# Install the optional local-model dependencies.
python -m pip install -e '.[dev,semantic]'

# Select the retriever after the search subcommand.
python -m src.cli search "finding information" --retriever semantic
python -m src.cli search "finding information" --retriever keyword

# Explicit cache location and offline reuse.
python -m src.cli search "finding information" --retriever semantic --model-cache .cache/ask-my-notes/models
python -m src.cli search "finding information" --retriever semantic --model-cache .cache/ask-my-notes/models --offline
```

Add `--retriever {keyword,semantic}` to the `search` subparser, defaulting to `keyword`. Add search options `--model-cache PATH` and `--offline` for semantic mode. Reject explicitly supplied semantic-only options in keyword mode with an argparse usage error (exit 2), rather than ignoring them. Existing global document and chunk options retain their positions before `search`.

Keep result formatting unchanged. Under `--verbose`, report the chosen retriever and, for semantic search, model identifier/revision, cache location, and eligible chunk count to stderr.

A missing optional dependency must yield a concise installation instruction and exit 1. Missing offline assets, failed downloads, and expected model-loading/encoding failures must produce actionable stderr messages and exit 1, with no fallback and no normal traceback. Successful searches, including empty result sets, exit 0. Preserve the existing exit 1 for no loaded documents. Catch expected operational errors narrowly; do not hide programming bugs behind a blanket exception handler.

## Downloads, caching, and offline use

Use `.cache/ask-my-notes/models` relative to the working directory as the explicit default model cache; allow `--model-cache` to override it. Ignore generated cache assets in Git. Check existing ignore rules before adding redundant entries.

The first online semantic search may download model assets. Explain this in setup documentation and emit a concise loading notice to stderr before a potentially slow model load. Subsequent searches reuse cached assets, though online mode may still make network requests. Do not claim that a warm cache alone guarantees offline operation.

`--offline` must request local-only model loading and prohibit network access in the model-loading path. With a complete cache for the pinned revision, search must work with networking disabled. With an empty or incomplete cache, fail promptly and explain how to populate that same cache using an online semantic search.

Embedding inference stays on the user's machine; the only intended network use is fetching model assets. Ordinary keyword searches and the default unit-test suite must neither import semantic dependencies nor download a model. Store passage vectors in memory only, rebuilding them when a new process starts so edited notes are reflected automatically.

## Testing and comparison

### Deterministic tests

Use a fake encoder that returns small known vectors. Verify the observable ranking and cosine scores with hand-checkable examples, including identical, orthogonal, and opposite vectors. Avoid reproducing the implementation in test code.

Cover exact ties and limits; original text and metadata; query/chunk call counts; passage-index reuse; caller mutation; short-circuit inputs; all-invalid chunks; malformed vectors; punctuation/stop-word queries; and truncation warnings. Verify original sentences reach the encoder without keyword filtering.

CLI tests must cover default and explicit keyword selection, semantic selection, missing dependencies, invalid option combinations, cached/offline loading arguments, and expected operational failures. Use fakes for these tests so they run without network or model assets. Include a keyword-only environment check proving the base install still works without the optional extra.

### Real-model comparison

Create a small, fixed English corpus and at least six labeled queries: two exact-match queries, two paraphrases, and two queries with no relevant passage. Choose the expected source labels before running either retriever; do not relabel failures to improve the comparison. Ensure at least one paraphrase has no retained keyword overlap with its expected passage.

Keep this fixture outside the default `documents/` collection, in a documented Markdown or Python file with a TOC and explanations. Run both retrievers against identical chunks and record top-three sources and raw scores separately, alongside the model revision, package versions, command, and chunk settings.

The real-model acceptance target is that both exact-match queries rank their expected passage first, and both paraphrases place their expected passage in the top three, with at least one showing a keyword miss recovered by semantic search. If the target fails, investigate and document the failure; do not claim completion based only on fake-encoder tests.

For the unrelated queries, record the actual nearest passages and explain that this milestone has no reliable abstention mechanism. These are demonstrations of a limitation, not tests expecting an empty semantic result. Avoid exact floating-point score assertions in real-model tests.

Put the integration check behind an explicit pytest marker and exclude it from the default test run. An explicitly requested integration run must fail with setup guidance if prerequisites are missing, rather than silently skip and appear successful. Populate the cache deliberately first, then run the integration check offline with networking disabled.

## Documentation and teaching materials

Expected implementation files include `src/semantic.py`, `src/cli.py`, `pyproject.toml`, relevant tests, and cache ignore rules if needed. Update `src/models.py` only if contract documentation needs clarification; its public interface remains unchanged.

Update `README.md`, `PROJECT_OVERVIEW.md`, and `Decisions.md` with installation, commands, model/version choices, caching, empty-input differences, truncation, actual comparison results, and validation evidence.

Update all six learning companions: `concept.md`, `concepts-script.md`, `concept-presentation.html`, `python-for-dummies.md`, `python-for-dummies-script.md`, and `python-for-dummies-slideshow.html`. Explain vectors, normalization, cosine similarity, optional dependencies, lazy loading, and fake encoders with beginner-friendly examples. Keep chapter/slide numbering, TOCs, narration, embedded source snippets, and calculated outputs synchronized.

Every created or modified file must have a current TOC and extensive explanatory comments appropriate to its format:

- Python modules begin with a contents docstring and include function/class docstrings plus comments explaining data flow, numerical assumptions, lifecycle, and error handling.
- Tests explain fixture choices and the behavior each assertion protects.
- Markdown uses navigable contents and visible explanatory prose.
- HTML preserves navigable slide contents and includes comments explaining non-obvious interactions, with presenter notes for teaching details.
- Configuration uses supported comment syntax for contents and dependency/test-setting rationale.

Comments should explain why choices were made, rather than restating each line. Execute complete teaching examples and verify output; inspect changed HTML slides and interactive behavior when browser tooling is available, and report any verification limits honestly.

## Acceptance criteria

1. Existing commands default to keyword search and all existing tests still pass without the semantic extra installed.
2. Semantic mode returns `SearchResult` objects with original passages and metadata through the existing interface.
3. Fake-vector tests verify cosine ranking, exact tie-breaking, limits, validation failures, and index reuse.
4. Empty requests avoid model loading; nonblank stop-word/punctuation input follows the documented semantic behavior.
5. Optional dependencies load only when needed; missing dependencies and model failures produce the specified CLI messages and exit codes.
6. A pinned model revision is reused from the configured cache, and a real offline search succeeds with networking disabled.
7. Empty-cache offline mode fails promptly without a network attempt or keyword fallback.
8. The fixed real-model comparison meets the exact-match/paraphrase target and documents unrelated-query limitations.
9. Overlength inputs emit an accurate warning; original displayed passages remain unchanged.
10. Project and teaching documentation, examples, TOCs, and source excerpts match the delivered implementation.

## Definition of done

- [x] Implement the optional semantic dependency setup, encoder boundary, retriever, and CLI options.
- [x] Record tested dependency versions and pin the resolved model revision.
- [x] Pass the existing suite and all new deterministic tests without downloads.
- [x] Verify keyword-only installation and CLI behavior without semantic dependencies.
- [x] Run and document the real-model comparison and meet its acceptance target.
- [x] Verify warm-cache offline success and empty-cache offline failure with networking disabled.
- [x] Verify dependency, download, malformed-vector, and truncation error/warning behavior.
- [x] Update project documentation and all six learning companions, including runnable examples.
- [x] Give every changed file a current TOC and extensive explanatory comments or prose.
- [x] Review the final diff for scope, generated assets, source-snapshot accuracy, and unintended changes.
- [x] Record actual validation results and mark this specification implemented only after all required work is complete.


## Verification

All **39 deterministic tests** pass in both the keyword-only and semantic environments. All **3 explicit real-model tests** pass with DNS and socket connections blocked, covering the fixed labeled comparison and actual CLI warm/empty-cache behavior. Both exact matches and both paraphrases ranked their expected source first; keyword search missed both paraphrase targets.

The model revision is pinned in `src/semantic.py`; the actual dependency versions, raw scores, commands, fixture labels, and Python/platform details are recorded in [semantic-search-results.md](semantic-search-results.md). The original `.venv` remains keyword-only; `.venv-semantic` has the optional dependencies. Model assets live in the ignored project cache.

All six learning companions were updated. **26 runnable tutorial examples** produce their documented output. Both HTML decks pass JavaScript syntax, navigation-count, and unique-ID checks. The concept deck's displayed code and all 15 full-source snapshots match current files. Browser discovery returned no available browser, so visual slide rendering could not be checked; this is a verification limitation rather than a claim of visual approval.

The diff was reviewed for implementation scope, documentation consistency, and generated assets. Existing unrelated edits, including the working-tree change to `documents/History.md`, were left intact. No commit was created.
