# Ten difficult concepts in Ask My Notes

Ranked by the reasoning needed to understand and safely extend this project. This is currently a local keyword-search application; embeddings, answer generation, and retrieval evaluation are future work. “How to solve it” below distinguishes the existing approach from suggested improvements. References identify exact lines in the source snapshot reviewed on September 17, 2026; later edits may move them.

## Contents

1. [Overlapping chunk boundaries](#1-overlapping-chunk-boundaries)
2. [Corpus-dependent inverse document frequency](#2-corpus-dependent-inverse-document-frequency)
3. [Balancing relevance, repetition, and passage length](#3-balancing-relevance-repetition-and-passage-length)
4. [Tokenization and the limits of literal matching](#4-tokenization-and-the-limits-of-literal-matching)
5. [Source provenance and citation stability](#5-source-provenance-and-citation-stability)
6. [Pipeline contracts and the path toward RAG](#6-pipeline-contracts-and-the-path-toward-rag)
7. [Index lifecycle, consistency, and scaling](#7-index-lifecycle-consistency-and-scaling)
8. [Deterministic ranking and floating-point arithmetic](#8-deterministic-ranking-and-floating-point-arithmetic)
9. [Validation and failure semantics across layers](#9-validation-and-failure-semantics-across-layers)
10. [Testing correctness versus measuring retrieval quality](#10-testing-correctness-versus-measuring-retrieval-quality)

## 1. Overlapping chunk boundaries

**Where encountered:** Window validation and construction in [src/chunker.py:20–41](src/chunker.py#L20); the concrete boundary example in [tests/test_chunker.py:14–24](tests/test_chunker.py#L14).

**Why difficult:** Chunk size controls how much context a result contains, while overlap trades additional context for duplicated text and more index entries. The stride is `chunk_size - overlap`, not the chunk size. With seven words, size four, and overlap one, starts are 0, 3, and 6. The final one-word chunk repeats text already present in the previous chunk; the existing test explicitly expects it. Whitespace splitting also loses formatting and does not respect sentence boundaries.

**How to solve it:** Trace start offsets and slices on a short example before tuning defaults. The implementation ensures `chunk_size > 0` and `0 <= overlap < chunk_size`, keeping the stride positive. Evaluate size and overlap together against representative queries. If redundant tail chunks are undesirable, a future change can stop after a window reaches the document end, with an intentional update to the current test. Sentence-aware splitting would require a separate boundary policy.

## 2. Corpus-dependent inverse document frequency

**Where encountered:** Per-chunk term counts and document-frequency construction in [src/search.py:34–47](src/search.py#L34); flattening documents into the indexed chunk collection in [src/chunker.py:45–57](src/chunker.py#L45).

**Why difficult:** “Document frequency” here counts chunks containing a term, not source files or total occurrences. Repeating a word ten times in one chunk increments its frequency only once. Chunking therefore changes the statistical corpus: overlapping text and long files contribute multiple entries, so changing overlap can change scores even for otherwise unchanged passages.

**How to solve it:** Read the formula as `idf(t) = log((1 + N) / (1 + df(t))) + 1`, where `N` is the number of chunks and `df(t)` counts chunks containing the term. The implementation iterates each counter's keys to count presence once, and smooths the ratio. For example, with three chunks, a term in every chunk has weight 1; one appearing in a single chunk has weight `1 + log(2)`. Rebuild these statistics when the corpus or chunking changes. Compare rankings using the same corpus and configuration.

## 3. Balancing relevance, repetition, and passage length

**Where encountered:** Query deduplication in [src/search.py:58–61](src/search.py#L58), matching and scoring in [src/search.py:65–75](src/search.py#L65), and the ranking example in [tests/test_search.py:13–28](tests/test_search.py#L13).

**Why difficult:** The ranking combines three competing effects: query-term coverage, term rarity, and chunk length. More matching occurrences help only up to a cap of three, but all indexed tokens still contribute to the length penalty. Repeating a query word has no effect because query terms form a set. This is a custom TF-IDF-inspired heuristic, not cosine similarity or a calibrated confidence probability.

**How to solve it:** Expand the implementation into `score(c, q) = sum(min(tf(t,c), 3) * idf(t) for matching query terms t) / sqrt(token_count(c))`. Calculate contributions on tiny passages to isolate each effect. No-match chunks are skipped before division, so a scored chunk necessarily has a positive token count. For future tuning, compare relevant long passages, short partial matches, and repeated keywords; use labeled queries rather than assuming a larger raw score means better retrieval across different corpora.

## 4. Tokenization and the limits of literal matching

**Where encountered:** ASCII token pattern and normalization in [src/search.py:14–24](src/search.py#L14); shared passage/query tokenization in [src/search.py:38–41](src/search.py#L38) and [src/search.py:58–66](src/search.py#L58). The corpus contains Chinese characters in [documents/History.md:5](documents/History.md#L5). The proposed stop-word exercise is in [README.md:76–78](README.md#L76).

**Why difficult:** Retrieval compares normalized tokens, not meanings. `document` and `documents` differ; punctuation splits terms; the `[a-z0-9]+` pattern excludes Chinese characters and does not preserve accented words intact. Chunking uses whitespace words, whereas scoring counts regex tokens, so “chunk length” has two different meanings. Common question words can match even when the important topic does not.

**How to solve it:** Inspect `tokenize()` output for both a query and its expected passage when diagnosing misses. Keep normalization identical at indexing and query time. Future improvements can add a tested stop-word policy or language-appropriate tokenization, followed by index rebuilding. Stemming, synonyms, and semantic retrieval require explicit additional behavior; none is currently implemented. Test multilingual text and punctuation before broadening the supported corpus.

## 5. Source provenance and citation stability

**Where encountered:** Immutable data records in [src/models.py:13–47](src/models.py#L13); relative source paths in [src/loader.py:30–35](src/loader.py#L30); propagation through chunk creation in [src/chunker.py:35–40](src/chunker.py#L35); printed references in [src/cli.py:63–67](src/cli.py#L63).

**Why difficult:** Text is transformed from a whole document into normalized windows, but a result must remain traceable to its origin. A relative filename and chunk number identify a passage only within a particular collection and chunking configuration. Editing a document or changing chunk size can change those numbers. The current model does not preserve original line numbers or character offsets.

**How to solve it:** Preserve source metadata at each transformation, as the current loader, chunker, and result wrapper do. Frozen dataclasses prevent ordinary field reassignment. For durable citations in a future answer generator, add document identity/version and original-text offsets before whitespace normalization loses that information. Treat today's displayed chunk references as navigation hints for the current collection, not permanent source-line citations.

## 6. Pipeline contracts and the path toward RAG

**Where encountered:** Retriever contract in [src/models.py:50–63](src/models.py#L50); concrete inheritance in [src/search.py:27–35](src/search.py#L27); orchestration in [src/cli.py:48–67](src/cli.py#L48); explicitly unimplemented extensions in [PROJECT_OVERVIEW.md:64–66](PROJECT_OVERVIEW.md#L64).

**Why difficult:** Separating ingestion, chunking, retrieval, and presentation makes later extensions manageable, but an interface alone does not remove all coupling. The CLI directly constructs `KeywordRetriever`. The base class raises `NotImplementedError`; it is not an abstract base class that prevents instantiation. Also, retrieving relevant passages is only one stage of retrieval-augmented generation (RAG), not answer generation itself.

**How to solve it:** Follow the current flow `Document -> DocumentChunk -> SearchResult` and preserve the `search(query, limit)` result contract in another retriever. A future factory or injected retriever can replace the CLI's concrete construction. Introduce answer generation as a separate consumer of retrieved passages and their provenance. Define empty-result, ordering, and limit behavior consistently across implementations, and evaluate retrieval before relying on it to ground generated answers.

## 7. Index lifecycle, consistency, and scaling

**Where encountered:** Whole-file loading in [src/loader.py:23–34](src/loader.py#L23); index initialization in [src/search.py:34–47](src/search.py#L34); full chunk scan in [src/search.py:63–75](src/search.py#L63); per-invocation reconstruction in [src/cli.py:47–57](src/cli.py#L47).

**Why difficult:** Precomputing token counts saves repeated tokenization during queries, but requires the counts, IDF statistics, and chunks to describe the same snapshot. `self.chunks = chunks` retains the caller's mutable list. Mutating that list later can misalign it with `term_counts`, while `zip` silently stops at the shorter input. Each CLI invocation currently reloads and indexes everything, and each query scans every chunk.

**How to solve it:** For the current CLI, keep construction and search together and avoid mutating the chunk list; the existing execution flow does this. A future reusable service should copy or freeze the collection and rebuild or atomically replace all index state after edits. For larger collections, an inverted index can locate candidate chunks without scanning every passage. Persistent caching would need invalidation based on file contents, tokenizer rules, and chunk settings, not just filenames.

## 8. Deterministic ranking and floating-point arithmetic

**Where encountered:** Sorted file traversal in [src/loader.py:24–25](src/loader.py#L24); set-based matched terms and floating-point summation in [src/search.py:59–74](src/search.py#L59); result sort key in [src/search.py:77–85](src/search.py#L77).

**Why difficult:** Stable ordering requires controlling both scores and tie-breaking. The explicit key sorts by descending score, then source, then chunk number. However, matched terms are a set, whose iteration order can vary between processes. Floating-point addition depends on order, so extremely close scores can still vary in their last bits even with deterministic tie-breakers.

**How to solve it:** Retain sorted traversal and the explicit secondary keys. If strict cross-process reproducibility is needed, a future change should sum contributions in sorted term order, optionally using `math.fsum` for improved numerical accuracy. Verify exactly tied results with a fixture and near-tied results across process hash seeds. Do not sort by the CLI's three-decimal display value: formatting can hide differences in the actual scores.

## 9. Validation and failure semantics across layers

**Where encountered:** CLI argument types in [src/cli.py:25–33](src/cli.py#L25); empty-collection and no-match exit behavior in [src/cli.py:48–61](src/cli.py#L48); chunk parameter checks in [src/chunker.py:20–23](src/chunker.py#L20); early search returns in [src/search.py:55–61](src/search.py#L55); UTF-8 file reads in [src/loader.py:30–34](src/loader.py#L30).

**Why difficult:** Syntactically valid input can still violate domain rules. `argparse` accepts negative integers, while the chunker rejects invalid sizes/overlap. A non-positive result limit intentionally returns no results. The CLI returns 1 for no loaded documents, but 0 for no matches. Invalid chunk settings and file read/decode errors are not caught by the CLI. Collection-level chunk validation is skipped when `chunk_documents` receives an empty list because validation occurs only inside the per-document call ([src/chunker.py:53–57](src/chunker.py#L53)).

**How to solve it:** Separate invalid configuration, ingestion failure, and a valid search with zero matches. Preserve the documented distinction between empty search results and setup problems. Future CLI hardening can validate configuration before loading, catch expected I/O and validation exceptions, and provide concise messages with deliberate exit codes. Choose and test whether unreadable files fail the whole search or are logged and skipped; the current loader propagates read failures.

## 10. Testing correctness versus measuring retrieval quality

**Where encountered:** Loader fixture in [tests/test_loader.py:11–22](tests/test_loader.py#L11); chunk expectations and invalid overlap in [tests/test_chunker.py:14–31](tests/test_chunker.py#L14); ranking and empty-query tests in [tests/test_search.py:13–33](tests/test_search.py#L13); future evaluation scope in [PROJECT_OVERVIEW.md:64–66](PROJECT_OVERVIEW.md#L64).

**Why difficult:** Five focused tests establish selected behaviors, but do not prove that real questions retrieve useful evidence. The ranking fixture checks one relative ordering. The empty-query test uses an empty index, so it cannot independently establish empty-query behavior against populated data. Overlap can also let several nearly identical passages occupy the top results, making result count a poor proxy for useful coverage.

**How to solve it:** Keep small, interpretable fixtures for algorithmic correctness. Future tests should isolate populated-index empty queries, punctuation-only queries, zero-token chunks, non-positive limits, tied scores, invalid sizes, and ingestion errors. Separately build a small set of representative queries with labeled relevant passages and measure how often relevant evidence appears in the top results, including diversity across sources. Use that evaluation to compare chunking and ranking changes. These proposed tests and evaluation workflows are not part of the current suite.
