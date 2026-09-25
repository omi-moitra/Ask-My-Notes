# Twelve difficult concepts in Ask My Notes

Ranked by the reasoning needed to understand and safely extend this project. This is a local application with default keyword search, optional semantic embeddings, and opt-in hybrid rank fusion. A small labeled comparison is implemented; answer generation and broad retrieval evaluation remain future work. “How to solve it” below distinguishes the existing approach from suggested improvements. References identify exact lines in the source snapshot reviewed on September 23, 2026; later edits may move them.

## Contents

1. [Overlapping chunk boundaries](#1-overlapping-chunk-boundaries)
2. [Corpus-dependent inverse document frequency](#2-corpus-dependent-inverse-document-frequency)
3. [Balancing relevance, repetition, and passage length](#3-balancing-relevance-repetition-and-passage-length)
4. [Tokenization and the limits of literal matching](#4-tokenization-and-the-limits-of-literal-matching)
   - [Stop-word filtering in practice](#stop-word-filtering-in-practice)
5. [Source provenance and citation stability](#5-source-provenance-and-citation-stability)
6. [Pipeline contracts and the path toward RAG](#6-pipeline-contracts-and-the-path-toward-rag)
7. [Index lifecycle, consistency, and scaling](#7-index-lifecycle-consistency-and-scaling)
8. [Deterministic ranking and floating-point arithmetic](#8-deterministic-ranking-and-floating-point-arithmetic)
9. [Validation and failure semantics across layers](#9-validation-and-failure-semantics-across-layers)
10. [Testing correctness versus measuring retrieval quality](#10-testing-correctness-versus-measuring-retrieval-quality)
11. [Embeddings, cosine similarity, and local model lifecycle](#11-embeddings-cosine-similarity-and-local-model-lifecycle)
    - [Compare the three retrieval modes](#compare-the-three-retrieval-modes)
12. [Rank fusion and candidate depth](#12-rank-fusion-and-candidate-depth)

- [Finding and running the checks](#finding-and-running-the-checks)

## 1. Overlapping chunk boundaries

**Where encountered:** Window validation and construction in [src/chunker.py:20–41](src/chunker.py#L20); the concrete boundary example in [tests/test_chunker.py:14–24](tests/test_chunker.py#L14).

**Why difficult:** Chunk size controls how much context a result contains, while overlap trades additional context for duplicated text and more index entries. The stride is `chunk_size - overlap`, not the chunk size. With seven words, size four, and overlap one, starts are 0, 3, and 6. The final one-word chunk repeats text already present in the previous chunk; the existing test explicitly expects it. Whitespace splitting also loses formatting and does not respect sentence boundaries.

**How to solve it:** Trace start offsets and slices on a short example before tuning defaults. The implementation ensures `chunk_size > 0` and `0 <= overlap < chunk_size`, keeping the stride positive. Evaluate size and overlap together against representative queries. If redundant tail chunks are undesirable, a future change can stop after a window reaches the document end, with an intentional update to the current test. Sentence-aware splitting would require a separate boundary policy.

## 2. Corpus-dependent inverse document frequency

**Where encountered:** Per-chunk term counts and document-frequency construction in [src/search.py:46–61](src/search.py#L46); flattening documents into the indexed chunk collection in [src/chunker.py:45–57](src/chunker.py#L45).

**Why difficult:** “Document frequency” here counts chunks containing a term, not source files or total occurrences. Repeating a word ten times in one chunk increments its frequency only once. Chunking therefore changes the statistical corpus: overlapping text and long files contribute multiple entries, so changing overlap can change scores even for otherwise unchanged passages.

**How to solve it:** Read the formula as `idf(t) = log((1 + N) / (1 + df(t))) + 1`, where `N` is the number of all original chunks, including stop-word-only chunks, and `df(t)` counts chunks containing the term. The implementation iterates each counter's keys to count presence once, and smooths the ratio. For example, with three chunks, a term in every chunk has weight 1; one appearing in a single chunk has weight `1 + log(2)`. Rebuild these statistics when the corpus or chunking changes. Compare rankings using the same corpus and configuration.

## 3. Balancing relevance, repetition, and passage length

**Where encountered:** Query deduplication in [src/search.py:72–76](src/search.py#L72), matching and scoring in [src/search.py:80–92](src/search.py#L80), and the ranking example in [tests/test_search.py:21–36](tests/test_search.py#L21).

**Why difficult:** The ranking combines three competing effects: query-term coverage, term rarity, and chunk length. More matching occurrences help only up to a cap of three, but all retained (non-stop-word) tokens still contribute to the length penalty. Repeating a query word has no effect because query terms form a set. This is a custom TF-IDF-inspired heuristic, not cosine similarity or a calibrated confidence probability.

**How to solve it:** Expand the implementation into `score(c, q) = sum(min(tf(t,c), 3) * idf(t) for matching query terms t) / sqrt(retained_token_count(c))`. Calculate contributions on tiny passages to isolate each effect. No-match chunks are skipped before division, so a scored chunk necessarily has a positive token count. For future tuning, compare relevant long passages, short partial matches, and repeated keywords; use labeled queries rather than assuming a larger raw score means better retrieval across different corpora.

## 4. Tokenization and the limits of literal matching

**Where encountered:** ASCII token pattern and normalization in [src/search.py:15–34](src/search.py#L15); shared passage/query tokenization in [src/search.py:50–53](src/search.py#L50) and [src/search.py:72–81](src/search.py#L72). The corpus contains Chinese characters in [documents/History.md:5](documents/History.md#L5). The completed policy is documented in [README.md](README.md#stop-word-filtering).

**Why difficult:** Retrieval compares normalized tokens, not meanings. `document` and `documents` differ; punctuation splits terms; the `[a-z0-9]+` pattern excludes Chinese characters and does not preserve accented words intact. Chunking uses whitespace words, whereas scoring counts regex tokens, so “chunk length” has two different meanings. The fixed stop-word filter now excludes common question words such as `how` and `is`; it can also discard words that matter in a title or phrase.

**How to solve it:** Inspect `tokenize()` output for both a query and its expected passage when diagnosing misses. Keep normalization identical at indexing and query time. The shared tokenizer already excludes the 26-word immutable `STOP_WORDS` vocabulary. Language-appropriate tokenization remains future work and would require index rebuilding. Keyword mode still has no stemming or synonym expansion. The separate semantic retriever uses the model’s own tokenizer and preserves whole sentences, including stop words. Test multilingual text and punctuation before broadening the supported corpus.


### Stop-word filtering in practice

The tokenizer lowercases, extracts ASCII alphanumeric tokens, then removes exact matches in the fixed vocabulary. `THE theory is useful` becomes `['theory', 'useful']`; filtering `the` does not remove the substring in `theory`. Numbers, repeated meaningful tokens, and `no`, `not`, and `never` remain. Retaining negation does not give the system an understanding of sentence meaning.

In keyword mode, both passages and queries follow this policy. `how is retrieval` and `retrieval` therefore produce identical results and scores in the same index. Chunk boundaries and displayed passage text stay intact. Only the searchable representation changes. A stop-word-only query returns no results; a stop-word-only passage cannot match and is skipped before division.

| Passage | Before score (rank) | After score (rank) |
| --- | --- | --- |
| `how is how is how is` | 3.442672 (1) | No match |
| `retrieval finds useful passages` | 0.702733 (2) | 0.702733 (1) |

These measured results use query `how is retrieval` against exactly these two chunks. The filter removes a false match; it does not guarantee better relevance for every query. Counts and length penalties use retained tokens, while IDF still uses the total number of original chunks. See the [reproduction example](README.md#before-and-after-comparison) and [completed spec](ai/stop-word-filter-spec.md).

## 5. Source provenance and citation stability

**Where encountered:** Immutable data records in [src/models.py:13–48](src/models.py#L13); relative source paths in [src/loader.py:30–35](src/loader.py#L30); propagation through chunk creation in [src/chunker.py:35–40](src/chunker.py#L35); printed references in [src/cli.py:91–95](src/cli.py#L91).

**Why difficult:** Text is transformed from a whole document into normalized windows, but a result must remain traceable to its origin. A relative filename and chunk number identify a passage only within a particular collection and chunking configuration. Editing a document or changing chunk size can change those numbers. The current model does not preserve original line numbers or character offsets.

**How to solve it:** Preserve source metadata at each transformation, as the current loader, chunker, and result wrapper do. Frozen dataclasses prevent ordinary field reassignment. For durable citations in a future answer generator, add document identity/version and original-text offsets before whitespace normalization loses that information. Treat today's displayed chunk references as navigation hints for the current collection, not permanent source-line citations.

## 6. Pipeline contracts and the path toward RAG

**Where encountered:** Retriever contract in [src/models.py:51–65](src/models.py#L51); concrete inheritance in [src/search.py:39–47](src/search.py#L39); orchestration in [src/cli.py:58–95](src/cli.py#L58); explicitly unimplemented extensions in [future extensions](PROJECT_OVERVIEW.md#future-extension-points).

**Why difficult:** Separating ingestion, chunking, retrieval, and presentation makes later extensions manageable, but an interface alone does not remove all coupling. The CLI now selects `KeywordRetriever`, `SemanticRetriever`, or `HybridRetriever` with `--retriever`, while preserving their shared result shape. The base class raises `NotImplementedError`; it is not an abstract base class that prevents instantiation. Also, retrieving relevant passages is only one stage of retrieval-augmented generation (RAG), not answer generation itself.

**How to solve it:** Follow the current flow `Document -> DocumentChunk -> SearchResult` and preserve the `search(query, limit)` result contract in another retriever. The CLI keeps retriever selection at its boundary; neither implementation owns loading files or rendering results. Introduce answer generation as a separate consumer of retrieved passages and their provenance. Define empty-result, ordering, and limit behavior consistently across implementations, and evaluate retrieval before relying on it to ground generated answers.

## 7. Index lifecycle, consistency, and scaling

**Where encountered:** Whole-file loading in [src/loader.py:23–34](src/loader.py#L23); index initialization in [src/search.py:46–61](src/search.py#L46); full chunk scan in [src/search.py:78–92](src/search.py#L78); per-invocation reconstruction in [src/cli.py:57–85](src/cli.py#L57).

**Why difficult:** Precomputing token counts saves repeated tokenization during queries, but requires the counts, IDF statistics, and chunks to describe the same snapshot. In keyword mode, `self.chunks = chunks` retains the caller's mutable list. Semantic mode instead snapshots the collection into a tuple. Mutating the keyword retriever’s caller list later can misalign it with `term_counts`, while `zip` silently stops at the shorter input. Each CLI invocation reloads documents; keyword mode builds counts immediately, while semantic mode builds vectors only when needed. Each actual query scans its passage index.

**How to solve it:** For the current CLI, keep construction and search together and avoid mutating the chunk list; the existing execution flow does this. A future reusable service should copy or freeze the collection and rebuild or atomically replace all index state after edits. For larger collections, an inverted index can locate candidate chunks without scanning every passage. Persistent caching would need invalidation based on file contents, tokenizer rules, and chunk settings, not just filenames.

## 8. Deterministic ranking and floating-point arithmetic

**Where encountered:** Sorted file traversal in [src/loader.py:24–25](src/loader.py#L24); set-based matched terms and floating-point summation in [src/search.py:73–91](src/search.py#L73); result sort key in [src/search.py:94–102](src/search.py#L94).

**Why difficult:** Stable ordering requires controlling both scores and tie-breaking. The explicit key sorts by descending score, then source, then chunk number. However, matched terms are a set, whose iteration order can vary between processes. Floating-point addition depends on order, so extremely close scores can still vary in their last bits even with deterministic tie-breakers.

**How to solve it:** Retain sorted traversal and the explicit secondary keys. For keyword scores, strict cross-process reproducibility would require summing contributions in a fixed term order, optionally with `math.fsum`. Semantic scoring already uses `math.fsum` over ordered vector coordinates, but model output can still vary slightly across hardware or library versions. Verify exactly tied results with a fixture and near-tied results across process hash seeds. Do not sort by the CLI's three-decimal display value: formatting can hide differences in the actual scores.

## 9. Validation and failure semantics across layers

**Where encountered:** CLI argument types in [src/cli.py:27–35](src/cli.py#L27); empty-collection and no-match exit behavior in [src/cli.py:58–89](src/cli.py#L58); chunk parameter checks in [src/chunker.py:20–23](src/chunker.py#L20); early search returns in [src/search.py:69–76](src/search.py#L69); UTF-8 file reads in [src/loader.py:30–34](src/loader.py#L30).

**Why difficult:** Syntactically valid input can still violate domain rules. `argparse` accepts negative integers, while the chunker rejects invalid sizes/overlap. A non-positive result limit intentionally returns no results. The CLI returns 1 for no loaded documents or expected semantic dependency/model failures, 2 for invalid option combinations, and 0 for a completed search, including an empty result list. Invalid chunk settings and file read/decode errors are not caught by the CLI. Collection-level chunk validation is skipped when `chunk_documents` receives an empty list because validation occurs only inside the per-document call ([src/chunker.py:53–57](src/chunker.py#L53)).

**How to solve it:** Separate invalid configuration, ingestion failure, and a valid search with zero matches. Preserve the documented distinction between empty search results and setup problems. Future CLI hardening can validate configuration before loading, catch expected I/O and validation exceptions, and provide concise messages with deliberate exit codes. Choose and test whether unreadable files fail the whole search or are logged and skipped; the current loader propagates read failures.

## 10. Testing correctness versus measuring retrieval quality

**Where encountered:** Loader fixture in [tests/test_loader.py:11–22](tests/test_loader.py#L11); chunk expectations and invalid overlap in [tests/test_chunker.py:14–31](tests/test_chunker.py#L14); ranking and empty-query tests in [tests/test_search.py:21–41](tests/test_search.py#L21); future evaluation scope in [future extensions](PROJECT_OVERVIEW.md#future-extension-points).

**Why difficult:** Sixty deterministic tests and five explicit model checks establish selected behaviors, but do not prove that real questions retrieve useful evidence. The ranking fixture checks one relative ordering. New tests isolate empty queries against populated indexes, verify equivalent filtered queries, and check limits, ties, preserved metadata, and normalization. Overlap can also let several nearly identical passages occupy the top results, making result count a poor proxy for useful coverage.

**How to solve it:** Keep small, interpretable fixtures for algorithmic correctness. The suite now covers populated-index empty queries, punctuation-only queries, zero-token chunks, nonpositive limits, and tied scores. Broader invalid-size and ingestion-error coverage can be added separately. Separately build a small set of representative queries with labeled relevant passages and measure how often relevant evidence appears in the top results, including diversity across sources. Use that evaluation to compare chunking and ranking changes. A six-query labeled comparison now checks exact matches, paraphrases, and unrelated questions; a broad quality benchmark remains future work.


### Finding and running the checks

A **unit test** gives a small piece of code known inputs and checks the expected result. For example, the hybrid tests supply prepared rankings and check exact reciprocal-rank scores. Fake encoders supply controlled vectors without loading a model. These checks establish behavior; they cannot establish that real questions retrieve useful evidence.

The current suite has **60 default test cases** and **5 separately selected integration cases**. A parametrized test runs the same function with several inputs, so cases and functions are different counts. Integration checks use the actual pinned, cached model and block network access. The separate 23-question evaluation measures retrieval quality against unchanged source-and-evidence labels: hybrid Hit@3 is 75%, versus semantic's 85%, even though the implementation tests pass.

| Test file | What it verifies |
| --- | --- |
| [test_loader.py](tests/test_loader.py) | Supported files, recursive loading, original text and source paths |
| [test_chunker.py](tests/test_chunker.py) | Overlap, source metadata, and invalid settings |
| [test_search.py](tests/test_search.py) | Keyword ranking, stop words, empty queries, and result limits |
| [test_semantic.py](tests/test_semantic.py) | Controlled vectors, model adapter behavior, index reuse, and errors |
| [test_hybrid.py](tests/test_hybrid.py) | Fusion arithmetic, identities, ties, candidate depth, and failures |
| [test_cli.py](tests/test_cli.py) | Mode selection, arguments, output, diagnostics, and exit statuses |
| [test_semantic_integration.py](tests/test_semantic_integration.py) | Actual model retrieval and complete/missing offline caches |

Run from the project root with the existing development environments:

```bash
# Default checks: no model dependency or download needed.
.venv/bin/python -m pytest -v
# Focus on the hybrid behavior.
.venv/bin/python -m pytest tests/test_hybrid.py -v
# Actual model checks: requires the semantic environment and populated cache.
.venv-semantic/bin/python -m pytest -m integration -v
# Quality measurement: writes the separate hybrid evaluation reports.
.venv-semantic/bin/python -m evaluations.run_retrieval
```

`-m pytest` runs pytest through the selected Python interpreter; `-v` lists individual cases. Pytest's `-m integration` selects the integration marker. Without that selection, `pyproject.toml` excludes model checks. `PASSED` means an expectation held, `FAILED` means it did not, and `deselected` means a case was intentionally outside that run. A missing required model cache fails an explicit integration run; it is not silently skipped.

## 11. Embeddings, cosine similarity, and local model lifecycle

**Where encountered:** [src/semantic.py](src/semantic.py), [semantic unit tests](tests/test_semantic.py), and the [measured comparison](ai/semantic-search-results.md).

**Why difficult:** An embedding replaces a sentence with a learned numeric representation. Its coordinates are not simple named properties that we can interpret individually. Similar directions can indicate related meanings, but the model can still select an irrelevant passage. This changes the meaning of “no match”: unlike exact keyword overlap, every nonblank semantic query can have nearest neighbors.

**How to solve it:** Separate model behavior from vector arithmetic. For vectors `a` and `b`, cosine is `dot(a, b) / (length(a) * length(b))`. Normalize each vector to length one, then take its dot product. `[3, 4]` becomes `[0.6, 0.8]`; compared with `[1, 0]`, its cosine is `0.6`. Equal directions score 1, perpendicular directions 0, and opposite directions -1. These are similarities, not probabilities. The code validates dimensions and finite nonzero norms before scoring.

A fake encoder with known vectors proves the arithmetic and index lifecycle without downloads. The real model proves a different claim: it can recover the two predefined paraphrase targets despite no retained keyword overlap. Both ranked first in the recorded comparison. Neither type of test substitutes for the other.

**Lifecycle:** The optional adapter imports Sentence Transformers only on actual encoding, loads a pinned model on CPU, and reuses it. The retriever snapshots nonblank chunks and caches their vectors in memory after successful validation. Each query gets a new vector; a new CLI process rebuilds the passage index. Downloaded model assets persist in the model cache. `--offline` resolves a local pinned snapshot before construction; network-blocked tests verify success and missing-cache failure.

**Text and failure policy:** Semantic input bypasses the keyword stop-word filter. The model tokenizer measures word pieces; overlength inputs are warned about and truncated, while full original text remains available for display. Blank queries, empty corpora, and nonpositive limits avoid loading entirely. Nonblank punctuation and stop-word queries are encoded normally. There is no relevance cutoff, and negative scores are eligible when they fall in the requested top results. Dependency and model failures are reported rather than silently falling back; hybrid preserves this behavior even if its keyword branch found matches.

**Run it:** After installing the semantic extra and populating its cache, use `python -m src.cli search "finding information" --retriever semantic --offline`. Compare source rankings with keyword mode, not numeric scores across methods. See [the spec](ai/semantic-search-spec.md) for scope and [the report](ai/semantic-search-results.md) for reproducible evidence and limitations.


### Compare the three retrieval modes

| Behavior | Keyword (default) | Semantic | Hybrid |
| --- | --- | --- | --- |
| Representation | Retained literal token counts | Original-text embeddings | Both branch rankings |
| Stop words | Removed from matching | Kept for context | Each branch keeps its own policy |
| Score | Capped counts × rarity / retained-length square root | Cosine similarity | Sum of `1 / (60 + rank)` contributions |
| No keyword matches | No results | Nearest passages remain eligible | Semantic-only contributions remain eligible |
| Blank query/nonpositive limit | No results | No model load | Neither branch searched |
| Disk cache | None | Pinned model assets | Same semantic model cache |
| Candidate depth | Actual matching chunks | Eligible chunks | Full union before final limit |
| Irrelevant queries | Can match unrelated literal terms | Always has nearest neighbors | Can promote weak literal matches; no threshold |

Trace the same query through all three modes before comparing rankings. Scores across modes are not comparable. The [recorded comparison](ai/semantic-search-results.md) shows `How can I recover deleted computer documents?` missing `backup.md` with keyword search and ranking it first with semantic search. That is evidence for this fixed case, not a general accuracy guarantee.


## 12. Rank fusion and candidate depth

**Where encountered:** [src/hybrid.py](src/hybrid.py), [hybrid tests](tests/test_hybrid.py), and [the three-method evaluation](evaluations/hybrid-results.md).

**Why difficult:** Keyword and cosine scores have incompatible meanings. Adding them lets arbitrary numerical scales control ranking. RRF instead treats each returned position as a vote: a passage at rank 1 contributes `1/61`, rank 2 contributes `1/62`, and a missing passage contributes zero. Agreement across methods can help, but two weak votes can defeat one strong semantic result.

**How to solve it:** Trace the actual lists, not just the displayed scores. Keyword `[A, B]` and semantic `[C, A]` produce A at `1/61 + 1/62`, C at `1/61`, and B at `1/62`: fused order A, C, B. The helper accepts prepared lists so this arithmetic can be checked without any model. Raw input score magnitudes are ignored. Equal fused scores use source filename and chunk number.

**Candidate depth:** Hybrid requests the full eligible corpus from both branches before applying the display limit. A passage ranked second in both lists can beat two rank-one candidates that are lower in the other list. Restricting branch requests to the final top one would lose it. Full lists also ensure the top-one output is a prefix of the top-three output. This policy is deliberately simple for a small local corpus, not a scalable candidate-window design.

**Identity and lifecycle:** A dictionary keyed by `(source, chunk_number)` collapses identical duplicate inputs and rejects conflicting text. Equal text at different source positions stays distinct. The caller's list is copied, keyword receives a private list, and semantic retains its existing lazy vector cache. In prepared branch lists, a repeated identity votes only at its first position; later positions are not renumbered.

**A counterexample:** Keyword returns irrelevant A first; semantic returns relevant B first and A second. A receives `1/61 + 1/62`, beating B's `1/61`. This is mathematically correct fusion and worse relevance. A semantic failure is different: the whole hybrid search fails, rather than presenting a partial keyword result as hybrid.

**Measured result:** On the unchanged 23-question set, hybrid Hit@1/Hit@3 is 75%/75%, compared with keyword 75%/75% and semantic 80%/85%. Hybrid recovers one semantic miss but loses three semantic hits. In the six-query fixture its paraphrase answers fall from semantic rank one to hybrid ranks three and two. No labels or constants were adjusted to hide these regressions. Hybrid remains opt-in; three-decimal fusion scores are not confidence probabilities.
