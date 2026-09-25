# Feature Spec: Hybrid Search with Reciprocal Rank Fusion

Status: Implemented and verified — 2026-09-23
Created: 2026-09-23

## Table of contents

- [Purpose](#purpose)
- [Definitions](#definitions)
- [In scope](#in-scope)
- [Out of scope](#out-of-scope)
- [Architecture](#architecture)
- [Fusion rules](#fusion-rules)
- [Worked example](#worked-example)
- [CLI and failure behavior](#cli-and-failure-behavior)
- [Tests and evaluation](#tests-and-evaluation)
- [Documentation and teaching requirements](#documentation-and-teaching-requirements)
- [Acceptance criteria](#acceptance-criteria)
- [Definition of done](#definition-of-done)
- [Implementation verification](#implementation-verification)

## Purpose

Add an explicit hybrid retrieval mode that combines keyword and semantic rankings. Exact terms can provide useful evidence that embedding similarity misses; semantic retrieval can find paraphrases with no shared keywords. The feature lets users compare a combined ranking with both existing methods.

This follows [local semantic search](semantic-search-spec.md). Keyword remains the default. Hybrid search is an additional choice, not a promise of higher relevance on every question. This document specifies the next implementation; its completion checklist is intentionally unchecked.

## Definitions

- **Branch:** One existing retrieval method: keyword or semantic.
- **Rank:** A passage's one-based position in a branch's ordered results.
- **Reciprocal rank fusion (RRF):** A score formed by adding a reciprocal contribution from each branch that returned a passage. The original branch score magnitudes are not combined.
- **Chunk identity:** The pair `(source, chunk_number)` within one corpus snapshot. Equal text in different files or chunk positions remains distinct evidence.
- **Candidate set:** The union of passages returned by either branch before the final result limit is applied.
- **Rank constant:** The fixed positive number added to each rank in the reciprocal formula. It controls how strongly adjacent ranks differ; it is not a confidence threshold.

## In scope

- Add `HybridRetriever` implementing the existing `Retriever.search(query, limit)` interface.
- Compose the existing keyword and semantic retrievers over the same stable chunk snapshot.
- Fuse rankings using equal-weight RRF, with a named fixed constant of 60.
- Add `--retriever hybrid`, preserving current keyword and semantic commands.
- Reuse the semantic extra, pinned model, cache, offline mode, validation, and truncation warnings.
- Add deterministic tests for fusion and orchestration, plus explicit offline real-model checks.
- Extend the existing evaluation to compare all three methods on identical corpus snapshots and labels.
- Update project documentation and all concepts/Python learning companions, with accurate TOCs and extensive explanations.

## Out of scope

- Adding or averaging keyword and cosine scores, score normalization, configurable weights, or parameter tuning.
- CLI options for rank constants, candidate windows, or selecting alternative models.
- Rerankers, relevance thresholds, automatic fallback, or claims that returned passages necessarily answer the question.
- Deduplicating overlapping passages by text similarity or enforcing source diversity.
- Persistent passage indexes, vector databases, concurrent branch execution, or scaling infrastructure.
- Changing the existing keyword stop-word policy, semantic model, ingestion, or chunk boundaries.
- LLM-generated answers, PDFs, web interfaces, or API services.

## Architecture

Create `src/hybrid.py` with the retriever and a small pure fusion helper. Keep branch algorithms in their existing modules. Preserve `SearchResult` and `DocumentChunk`; a hybrid result's `score` holds its RRF score, and its chunk retains original text and metadata.

Snapshot the supplied chunks before constructing either branch. Give the keyword branch its own list so later mutation of the caller's list cannot misalign its counts. Semantic retrieval already snapshots chunks and lazily builds its vectors. Reuse both branch instances for repeated searches; do not instantiate a model per query.

Use the same nonblank chunks for both branches. Whitespace-only chunks supplied directly through the Python API are excluded before construction. Duplicate input identities with identical text collapse to one canonical chunk. Conflicting text for the same identity is an input error: raise a clear `ValueError` before indexing. These rules belong to hybrid mode and do not change standalone behavior.

Permit a fake encoder through the existing semantic encoder boundary. The fusion helper should also accept prepared ranked results, making fusion arithmetic testable without a model or invented vector geometry. Do not add runtime model imports to hybrid module initialization.

## Fusion rules

### Scoring

For each candidate `c`, use:

```text
RRF(c) = sum(1 / (60 + rank_b(c)) for each branch b that returned c)
```

Ranks start at 1. A missing passage contributes zero from that branch. Both branches have equal weight. This uses the formula and rank constant described in the [original RRF paper](https://cormack.uwaterloo.ca/cormacksigir09-rrf.pdf); the paper's experimental performance is not a prediction for this project.

Treat each branch's returned order as authoritative, including its existing tie-breakers. Do not re-sort it using rounded scores, assign shared ranks to equal scores, or feed raw scores into the fusion formula. A semantic passage with zero or negative cosine still contributes if returned, as standalone semantic mode has no cutoff.

Count a chunk at most once per branch and once in the output. If a prepared branch list repeats an identity, only its first occurrence contributes, using its first position in that list. Reject conflicting text for the same identity rather than silently selecting a different source passage.

Sort candidates by descending full-precision RRF score, then source filename, then chunk number. Apply the requested final `limit` only after fusion. The score is neither a probability nor a value comparable with standalone keyword or semantic scores.

### Candidate depth

For this small local application, request up to `N` results from each branch, where `N` is the number of unique nonblank chunks in the hybrid snapshot. The keyword branch returns its actual matches; the semantic branch returns its full ranking. Do not fuse only each branch's final top three.

This deliberate full-corpus policy avoids an arbitrary candidate-window setting and makes changing `limit` affect only output length. For fixed inputs, `search(query, 1)` must equal the first result of `search(query, 3)`. It also reflects the current branches, which already scan their whole indexes. Larger-corpus candidate windows are future work, not an undocumented optimization.

Full rankings have a tradeoff: any keyword hit also appears in the semantic list and receives contributions from both branches. Even a weak literal match may then outrank a strong semantic-only result. Tests and evaluation must expose this behavior rather than hide it. A fixed RRF policy can be implemented correctly and still regress on a query.

### Empty requests and errors

Return `[]` for a blank/whitespace-only query, no eligible chunks, or a nonpositive limit, without invoking branch searches or loading the model.

For any other query, run both branches. If keyword returns no matches, fuse the semantic list alone: order stays semantic, but scores become reciprocal-rank values. A nonblank stop-word-only or punctuation-only query therefore may return passages. This is ordinary fusion, not an error fallback.

Propagate semantic dependency, loading, encoding, and invalid-vector failures through the existing `SemanticError` path. Do not return a partial keyword result when the semantic branch fails. Unknown programming failures must remain visible rather than being converted into empty results.

## Worked example

These are illustrative branch rankings, not measured model outputs:

| Chunk | Keyword rank | Semantic rank | RRF score |
| --- | --- | --- | --- |
| A | 1 | 2 | `1/61 + 1/62 = 0.03252247488101534` |
| B | 2 | absent | `1/62 = 0.016129032258064516` |
| C | absent | 1 | `1/61 = 0.01639344262295082` |

The fused order is A, C, B. Changing branch score magnitudes without changing their orders must leave the result unchanged. This helper example includes a keyword-only candidate to test generic union handling; the real semantic branch normally returns every eligible chunk under the full-corpus policy.

A second fixture must show a limitation: keyword ranks an irrelevant A first, while semantic ranks relevant B first and A second. A receives two votes and outranks semantic-only B. The test demonstrates a predictable ranking regression; it must not relabel A as relevant.

The existing three-decimal CLI display rounds close RRF scores together. Keep output formatting unchanged and sort on raw scores. Use full scores and component ranks in evaluation reports to explain differences hidden by display rounding.

## CLI and failure behavior

Proposed commands:

```bash
# No new extra or model download beyond the existing semantic setup.
python -m pip install -e '.[dev,semantic]'
python -m src.cli search "finding information" --retriever hybrid
python -m src.cli search "finding information" --retriever hybrid --offline
python -m src.cli search "finding information" --retriever hybrid --model-cache .cache/ask-my-notes/models --offline
```

Add `hybrid` to the search subparser's `--retriever` choices; retain `keyword` as its default. Permit `--model-cache` and `--offline` for semantic and hybrid modes, while continuing to reject them in keyword mode with exit 2. Preserve global option placement before `search`.

Reuse the same pinned model revision and cache. Online hybrid mode may download assets; offline mode must not access the network. The base installation and default tests must still work without the semantic extra. In this workspace `.venv` is keyword-only and `.venv-semantic` contains the model dependencies.

Preserve result formatting and exit meanings: 0 for a completed search including empty results, 1 for no loaded documents or expected model/dependency failures, and 2 for argument usage errors. Missing or incomplete offline assets must give guidance for populating the same cache. Do not silently drop a branch.

Under `--verbose`, log hybrid mode, rank constant, eligible corpus size, branch result counts, and existing semantic model/cache details to stderr. Do not add verbose diagnostics to ordinary stdout or expose implementation details in every displayed passage.

## Tests and evaluation

### Deterministic tests

Cover the worked union/rank example, score-magnitude independence, one-branch-empty and both-empty fusion, duplicate identities, conflicting text, exact RRF ties, deterministic secondary ordering, and no duplicate output chunks. Include equal text with different identities and ensure both remain eligible.

Test candidate depth separately from output limit: a passage below both requested output cutoffs can rise after fusion, so branch requests must use the eligible corpus size. Test prefix consistency across output limits. Verify original text/metadata, repeated-query index reuse, and immunity to caller list mutations.

Use a fake encoder to cover actual branch composition, zero-keyword-overlap queries, semantic stop-word/punctuation handling, and model-free early returns. Test that a semantic failure yields no partial keyword output. Retain all existing standalone regression tests.

CLI tests must cover explicit hybrid selection, defaults, semantic/hybrid cache and offline options, invalid keyword-only combinations, missing dependencies, expected model failures, exit statuses, and verbose diagnostics without real downloads.

### Existing six-query integration fixture

Run keyword, semantic, and hybrid over the unchanged [semantic fixture](../tests/fixtures/semantic_cases.py), using identical chunks and the pinned cached model. Preserve the existing exact/paraphrase labels and standalone checks. Record each expected passage's position under hybrid, including any regression relative to semantic mode.

Keep these real-model checks under the existing explicit `integration` marker. Block socket/DNS access, test complete-cache success and empty-cache failure, and fail with guidance when explicitly requested prerequisites are absent. Do not silently skip missing model assets.

### Twenty-three-question evaluation

Extend the existing [evaluation runner](../evaluations/run_retrieval.py) and [report](../evaluations/README.md) to include hybrid without replacing its original questions or evidence-phrase labels. Inspect the runner's current interface before editing it. Preserve current user-authored evaluation work and historical results; write the new three-way output to a distinct, clearly named result artifact such as `evaluations/hybrid-results.json`.

Rerun all three methods on the same current corpus and chunk settings. Record corpus hashes, model revision, tested versions, rank constant, candidate-depth policy, and commands. Historical percentages in an earlier report are not a same-corpus baseline if files changed.

Report Hit@1 and Hit@3 over answerable queries, and unrelated queries returning results separately. Preserve evidence-phrase matching rather than counting any chunk from the correct file as a hit. Record per-query expected-answer ranks and mark gains, ties, and regressions relative to each standalone mode. Include component ranks, full fusion scores, and passages for the top hybrid results so changes are explainable.

Do not fabricate a real-query improvement if none occurs. Completion requires a correct implementation and an honest comparison, not a predetermined aggregate win. If hybrid fails to improve this diagnostic set or regresses, document that finding and keep it opt-in. Do not tune constants, change labels, or change the default to make the milestone appear successful.

## Documentation and teaching requirements

Expected changes include `src/hybrid.py`, CLI choices/validation, focused tests, evaluation support, and documentation. No new runtime dependency is necessary. Clarify shared result-score documentation if needed without changing the interface.

Update README, project overview, and decision log with commands, full-corpus candidate policy, score meaning, offline requirements, actual results, and limitations. Store implementation validation in a new `ai/hybrid-search-results.md` report.

Update all six learning companions: `concept.md`, `concepts-script.md`, `concept-presentation.html`, `python-for-dummies.md`, `python-for-dummies-script.md`, and `python-for-dummies-slideshow.html`. Explain one-based ranks, reciprocal contributions, candidate union, identity-based deduplication, deterministic ties, and composition. Include a runnable model-free example and a case where fusion hurts relevance. Synchronize introductory explanations, source indexes, navigation, narration, source snapshots, and computed outputs.

Every created or modified file must have an accurate TOC and extensive explanatory comments appropriate to its format. Python modules and tests need contents docstrings, function/class docstrings, and comments explaining decisions and edge cases. Markdown needs navigable contents and substantive visible explanations. HTML needs current slide navigation, explanatory comments, and presenter notes. Configuration needs supported contents/comments. For generated JSON, use descriptive metadata plus a `contents` field mapping its sections and an explanation field; JSON does not support comments, so document its schema in the companion Markdown report.

Execute runnable teaching examples and verify their output. Check slide navigation, JavaScript, and source snapshots. Inspect changed slides visually when browser tooling is available, otherwise record that verification limitation explicitly.

## Acceptance criteria

1. Existing keyword and semantic commands retain their behavior; hybrid is an explicit third option.
2. Hybrid uses equal-weight RRF with constant 60 and one-based ranks, without combining raw scores.
3. Candidates come from full branch rankings for the same stable, unique, nonblank chunk snapshot; the final limit is applied after fusion.
4. Identity handling, original metadata, stable ties, limit prefixes, and repeated-query reuse satisfy deterministic tests.
5. Empty requests remain model-free; nonblank empty-keyword queries can use semantic results through normal fusion.
6. Semantic failures surface clearly without partial fallback, and offline behavior matches semantic mode.
7. Keyword-only installation and default tests remain free of semantic dependencies and network use.
8. Explicit real-model checks and the three-way 23-question evaluation run with unchanged labels and recorded corpus/model settings.
9. Gains and regressions are reported honestly, with at least one controlled example explaining why fusion can hurt.
10. Project docs and all learning companions match the delivered implementation, with verified examples, TOCs, and explanatory comments/prose.

## Definition of done

- [x] Implement the hybrid retriever, fusion helper, stable snapshot, and identity rules.
- [x] Add CLI selection, cache/offline validation, failure handling, and verbose diagnostics.
- [x] Pass all existing and new deterministic tests without model downloads.
- [x] Verify keyword-only operation without optional dependencies.
- [x] Pass explicit offline real-model checks, including complete and missing caches.
- [x] Run the six-query fixture across all three methods and record hybrid outcomes without relabeling.
- [x] Run the existing 23-question evaluation with all three methods and preserve historical results.
- [x] Document per-query gains/regressions, aggregate metrics, component ranks, versions, and corpus hashes.
- [x] Update project documentation and all six learning companions, with runnable examples and synchronized source excerpts.
- [x] Verify comments/TOCs, navigation, example outputs, and slide checks; record any visual-inspection limitation.
- [x] Review the final diff for scope and generated assets; record validation and only then mark this spec implemented.

## Implementation verification

See [validation results](hybrid-search-results.md) for 60 passing deterministic tests, five passing offline model checks, unchanged six-query and 23-question evaluations, teaching-example checks, and the visual-inspection limitation. Hybrid remains opt-in: Hit@3 was 75%, versus semantic search’s 85%. Historical results and evaluation labels were preserved. All 28 tutorial examples, both slide decks, and source snapshots passed their static checks.
