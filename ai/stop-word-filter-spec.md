# Feature Spec: Stop-Word Filtering

Status: Implemented and verified (2026-09-22)  
Created: 2026-09-22

## Table of contents

- [Purpose](#purpose)
- [Definitions](#definitions)
- [In scope](#in-scope)
- [Out of scope](#out-of-scope)
- [Required behavior](#required-behavior)
- [Implementation and documentation](#implementation-and-documentation)
- [Acceptance criteria](#acceptance-criteria)
- [Before-and-after comparison](#before-and-after-comparison)
- [Definition of done](#definition-of-done)

## Purpose

Improve the existing keyword retriever by excluding a small, explicit set of common English words from search matching and scoring. Before this feature, a query such as `how is retrieval` could match a passage solely because it contains `how` or `is`. Filtering these words lets the remaining terms determine relevance.

This is the follow-up exercise described in [README.md](../README.md). It remains a small, explainable learning feature using only Python's standard library at runtime.

## Definitions

- **Token:** A lowercase alphanumeric term produced by the existing regular expression in `src/search.py`.
- **Stop word:** A token in the fixed exclusion set defined below. This is a deliberately limited project vocabulary, not a claim that these words are irrelevant in every context.
- **Retained token:** A token remaining after stop-word filtering.
- **Stop-word-only query:** A query whose tokens are all excluded, leaving no searchable terms.
- **Chunk:** An overlapping passage carrying its original text, source filename, and one-based chunk number.

## In scope

- Add a named, immutable stop-word set in `src/search.py`.
- Apply the same filtering rules to document chunks and search queries through the shared `tokenize` function.
- Calculate term counts, document frequencies, and length normalization using retained tokens.
- Handle queries and chunks with no retained tokens safely.
- Add focused tests and a reproducible ranking comparison.
- Update the README, project overview, and decision log to explain the completed feature and its limitations.
- Provide extensive explanatory comments and a table of contents in every file created or modified for this feature.

## Out of scope

- Embeddings, semantic search, synonym expansion, stemming, or lemmatization.
- LLM answers, citations beyond existing passage metadata, or a full RAG pipeline.
- PDF ingestion, new file formats, web interfaces, or API services.
- External NLP libraries, new runtime dependencies, downloaded dictionaries, or language detection.
- User-configurable stop-word lists, CLI switches, and per-query filtering overrides.
- Changes to loading, chunk boundaries, the `Retriever` interface, or CLI output formatting.
- A general evaluation framework or broad changes to the ranking algorithm.
- Retrofitting unrelated repository files solely to add comments or tables of contents.

## Required behavior

### Fixed vocabulary

Use exactly this initial set so behavior is predictable and testable:

```text
a, an, and, are, as, at, be, by, does, for, from, how, in, is,
it, of, on, or, that, the, this, to, was, were, what, with
```

Keep negation words such as `no`, `not`, and `never`: removing them can discard meaningful distinctions. Explain that retained negation still does not give this literal keyword retriever an understanding of sentence meaning. Future vocabulary changes should be deliberate and accompanied by tests.

### Tokenization and indexing

Lowercase and extract alphanumeric tokens using the existing regular expression, then exclude exact matches in the stop-word set. Preserve the order and repetition of all remaining tokens. Do not remove substrings: excluding `the` must not remove `theory`.

Apply filtering to both indexed chunks and queries. Keep original chunk text and metadata intact so displayed passages and citations remain faithful to the source. Chunking still operates on the original words before retrieval filtering.

### Scoring and empty input

Keep the existing rarity weighting, repetition cap of three, query-term deduplication, and deterministic ordering by descending score, then source filename and chunk number. Use retained-token counts for the length-normalization denominator.

Keep the current total number of chunks in the inverse-document-frequency formula, including chunks with no retained tokens. Such chunks have no indexed terms and cannot match a query. Skip nonmatching chunks before calculating a score, preventing division by zero.

Return an empty result list for stop-word-only, blank, or punctuation-only queries. Preserve existing behavior for an empty corpus, unmatched queries, and nonpositive result limits. The CLI should use its existing no-results behavior.

Scores and rankings may change because common terms no longer contribute to matching or passage length. Scores need not be numerically comparable with the previous implementation.

## Implementation and documentation

Expected files:

| File | Planned change |
| --- | --- |
| `src/search.py` | Define the exclusion set, filter shared tokens, and explain scoring and empty-token behavior. |
| `tests/test_search.py` | Add behavioral coverage for filtering, ranking, and edge cases. |
| `README.md` | Document filtering, vocabulary, limitations, and the before-and-after example; replace the completed follow-up exercise. |
| `PROJECT_OVERVIEW.md` | Describe the new behavior and actual validation results. |
| `Decisions.md` | Record the vocabulary choice, symmetric filtering, normalization, and treatment of empty chunks. |

Every created or modified file must have an accurate TOC and extensive explanatory comments appropriate to its format:

- **Python:** Begin with a module docstring containing a contents list. Include function and class docstrings and substantial comments explaining purpose, data flow, algorithm choices, assumptions, and edge cases. Explain why shared filtering and the empty-token guard matter.
- **Tests:** Include a module contents list, descriptive test docstrings, and comments explaining fixture design and the regression each assertion protects against.
- **Markdown:** Include a navigable table of contents and explanatory prose under each substantive section. Use visible explanations rather than hiding important information in HTML comments.
- **Other text formats, if needed:** Use their supported comment syntax for a contents section and explanations. Avoid adding files in formats that cannot support these requirements unless necessary.

Comments must teach the reasoning behind the code, not merely restate individual statements. Update contents lists and explanations alongside implementation changes so they describe the final behavior.

## Acceptance criteria

1. Tokenizing `THE theory is useful` returns `['theory', 'useful']`, demonstrating case normalization and exact-token filtering.
2. Tokenization retains meaningful tokens, numbers, ordering, and duplicates; `not never no python python 123` remains unchanged as a token sequence.
3. Searching a nonempty corpus for `the is how` returns no results, even when those words appear in the original passages.
4. Within the same index, `how is retrieval` returns the same results and scores as `retrieval`.
5. A passage sharing only excluded words with a query is not returned.
6. Chunks containing only stop words do not cause errors, whether mixed with searchable chunks or forming the entire corpus.
7. Blank, punctuation-only, unmatched queries, empty corpora, and nonpositive limits return no results.
8. Result limits and deterministic tie-breaking continue to work. Original passage text, source, and chunk number are preserved.
9. Equivalent retained-token sequences produce equal scores even when one original passage has additional stop words, confirming retained-token normalization.
10. Existing tests and all new behavioral tests pass. Tests exercise public behavior without duplicating the scoring implementation.

## Before-and-after comparison

Use this controlled corpus and query to demonstrate the intended effect:

| Source | Chunk number | Text |
| --- | --- | --- |
| `filler.txt` | 1 | `how is how is how is` |
| `retrieval.md` | 1 | `retrieval finds useful passages` |

Query: `how is retrieval`.

With the original unfiltered implementation, the filler passage ranks first because repeated common words contribute to its score; the retrieval passage ranks second. After filtering, only the retrieval passage matches.

Record actual before-and-after results in the README during implementation, including the query and corpus so the comparison is reproducible. Add a regression test for the desired filtered result. A second production retriever or a permanent CLI option for unfiltered search is unnecessary.

This example demonstrates removal of a specific false match; it does not establish improved relevance for every possible query. Common words can be meaningful in titles or phrases, and this feature intentionally offers no override yet.

## Definition of done

- [x] All required behavior and acceptance criteria are implemented and covered by focused tests.
- [x] `.venv/bin/python -m pytest -q` passes, including the existing suite.
- [x] `.venv/bin/python -m src.cli search "How does retrieval work?"` returns relevant sample passages with original metadata.
- [x] `.venv/bin/python -m src.cli search "the is how"` follows the existing no-results path without error.
- [x] The controlled before-and-after comparison is run and documented with actual results.
- [x] Every created or modified file has a current TOC and extensive explanatory comments or prose as specified above.
- [x] README, project overview, and decision log accurately describe the delivered behavior and validation.
- [x] No runtime dependency, public interface, or unrelated feature is added.
- [x] The final diff is reviewed for scope, stale explanations, and unintended changes.


Verification on 2026-09-22: all 9 tests passed; both CLI smoke checks exited successfully. The controlled comparison and measured scores are recorded in the README. The implementation and documentation diff was reviewed for scope and consistency.
