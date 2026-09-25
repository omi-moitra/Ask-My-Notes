# Hybrid Search: Validation Results

Verified: 2026-09-23

## Contents

- [Setup and commands](#setup-and-commands)
- [Deterministic and offline checks](#deterministic-and-offline-checks)
- [Six-query comparison](#six-query-comparison)
- [Twenty-three-question evaluation](#twenty-three-question-evaluation)
- [Interpretation and limits](#interpretation-and-limits)
- [Teaching-material verification](#teaching-material-verification)

## Setup and commands

The implementation uses equal-weight reciprocal rank fusion with constant 60 and full rankings from both branches before applying the display limit. All modes share the existing chunker and original passage metadata. Keyword remains the CLI default; hybrid uses the existing optional semantic dependency and pinned CPU model.

Model: `sentence-transformers/all-MiniLM-L6-v2`, revision `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`.

Environment: Python 3.14.3 on macOS-26.5.2-arm64-arm-64bit-Mach-O. Dependency versions tested:

| Package | Version |
| --- | --- |
| huggingface-hub | 0.36.2 |
| numpy | 2.5.3 |
| scikit-learn | 1.9.1 |
| scipy | 1.18.1 |
| sentence-transformers | 5.1.2 |
| tokenizers | 0.22.2 |
| torch | 2.14.0 |
| transformers | 4.57.6 |

```bash
# No semantic dependency is installed in this base environment.
.venv/bin/python -m pytest -q
# Default tests also run in the optional-dependency environment.
.venv-semantic/bin/python -m pytest -q
# Explicit model tests prohibit DNS and socket connections.
.venv-semantic/bin/python -m pytest -m integration -s -q
# Fixed evidence-phrase labels, current notes, offline model loading.
.venv-semantic/bin/python -m evaluations.run_retrieval
# Use hybrid interactively once the existing pinned model cache is available.
.venv-semantic/bin/python -m src.cli search "finding information" --retriever hybrid --offline
```

A fresh environment needs `python -m pip install -e '.[dev,semantic]'` and one online semantic or hybrid search to populate the cache before using `--offline`. No additional dependency or model is introduced by hybrid mode. Python 3.10 remains the declared minimum; actual execution here used 3.14.3.

## Deterministic and offline checks

**60 default tests pass** in both environments, with 5 explicit model checks deselected. The base environment has no `sentence_transformers` package, and importing the CLI/hybrid module does not import it. Deterministic tests cover rank arithmetic, score independence, identity conflicts, duplicates, ties, full candidate depth, limit prefixes, caller mutation, index reuse, errors, and CLI wiring.

**5 explicit integration tests pass**, including the unchanged standalone semantic acceptance criteria, all-three-mode fixture comparison, semantic/hybrid warm-cache CLI success, and missing-cache failures. Socket connections and DNS lookups are prohibited and counted; no network attempt occurred. No missing prerequisite is silently skipped.

## Six-query comparison

The original six questions and labels were not changed. Rankings below are measured outcomes; expected-answer rank is shown for the top three. The exact cases remain first. The two paraphrases remain in hybrid's top three but drop from semantic rank one to ranks three and two.

| Question | Expected | Keyword answer rank | Semantic answer rank | Hybrid answer rank |
| --- | --- | --- | --- | --- |
| external drive restore lost data | backup.md | 1 | 1 | 1 |
| yeast ferments sugar | bread.md | 1 | 1 | 1 |
| How can I recover deleted computer documents? | backup.md | — | 1 | 3 |
| Why does a loaf expand during baking? | bread.md | — | 1 | 2 |
| What is the orbital period of Neptune? | none | — | — | — |
| Who won the 1998 football World Cup? | none | — | — | — |

Full measured hybrid top-three outputs (raw RRF scores):

- **external drive restore lost data** `backup.md`: 0.03278688524590164; `retrieval.md`: 0.016129032258064516; `plants.md`: 0.015873015873015872.
- **yeast ferments sugar** `bread.md`: 0.03278688524590164; `plants.md`: 0.016129032258064516; `retrieval.md`: 0.015873015873015872.
- **How can I recover deleted computer documents?** `retrieval.md`: 0.03252247488101534; `sleep.md`: 0.031754032258064516; `backup.md`: 0.01639344262295082.
- **Why does a loaf expand during baking?** `cycling.md`: 0.032266458495966696; `bread.md`: 0.01639344262295082; `plants.md`: 0.016129032258064516.
- **What is the orbital period of Neptune?** `cycling.md`: 0.01639344262295082; `retrieval.md`: 0.016129032258064516; `bread.md`: 0.015873015873015872.
- **Who won the 1998 football World Cup?** `retrieval.md`: 0.01639344262295082; `backup.md`: 0.016129032258064516; `bread.md`: 0.015873015873015872.


## Twenty-three-question evaluation

The existing 23 questions and evidence-phrase labels are unchanged. All three methods ran against the same 170 chunks (120 words, overlap 20). Historical `evaluations/results.json` was preserved byte-for-byte. The new [JSON report](../evaluations/hybrid-results.json) includes corpus hashes, component ranks, raw scores, and passages; [the readable report](../evaluations/hybrid-results.md) details each query.

| Method | Hit@1 (20 answerable) | Hit@3 (20 answerable) | Unrelated returning results |
| --- | --- | --- | --- |
| keyword | 75% | 75% | 3/3 |
| semantic | 80% | 85% | 3/3 |
| hybrid | 75% | 75% | 3/3 |

Relative to semantic, hybrid recovers the question about Garland's first childhood song, but loses top-three evidence for overlapping text segments, Li Jingsui's original name, and Garland's birthplace. That is **1 gain, 3 regressions, 16 ties** by answer rank within the top three. All 20 answerable outcomes tie keyword under that measure. Unrelated cases are excluded from gains/regressions and hit-rate denominators.

## Interpretation and limits

This full-corpus equal-weight policy did not improve aggregate retrieval quality. Every literal hit also appears in the semantic list and receives two reciprocal contributions, even if semantic similarity is weak or negative. A strong semantic-only answer receives one contribution and can lose. The pure-helper regression fixture demonstrates the same effect without a model. Neither labels nor the rank constant were tuned after observing results.

Hybrid is an additional mode, not a new default. Fusion scores are not probabilities and cannot be compared with keyword or cosine scores. Three-decimal display can hide score differences; sorting uses raw values. All modes returned unrelated passages on this diagnostic set; there is no abstention threshold. Small model score changes across hardware/library versions remain possible.

## Teaching-material verification

All six learning companions now explain rank fusion, candidate depth, identity handling, composition, and measured regressions. All **28 runnable tutorial examples** produced their documented output in the base environment. The concept deck has **30 slides**, and the Python deck has **26**. Checks passed for unique slide IDs, navigation metadata, JavaScript syntax, Markdown contents links, **312 displayed source lines**, and **18 complete source snapshots** against the current files.

An actual offline CLI run with `--verbose` succeeded and kept retriever, pinned-model, candidate-depth, and branch-count diagnostics on stderr. Historical evaluation results remain byte-identical. `git diff --check` passed.

**Visual inspection was unavailable:** no connected browser was available earlier, and the final browser runtime had no initialized agent; the advertised browser skill file was also absent. Static checks do not establish visual layout quality.
