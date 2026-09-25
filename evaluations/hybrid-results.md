# Hybrid retrieval evaluation

## Contents

- [Setup](#setup)
- [Metrics](#metrics)
- [Per-query comparison](#per-query-comparison)
- [Result schema and interpretation](#result-schema-and-interpretation)

## Setup

The original 23 questions and evidence-phrase labels are unchanged: 20 answerable and 3 unrelated. All modes use identical 120-word chunks with 20-word overlap. A hit requires the labeled evidence inside a returned chunk, not just the expected filename. This is a diagnostic set, not a general benchmark.

Run: `.venv-semantic/bin/python -m evaluations.run_retrieval`. The pinned model cache must be populated first; inference is offline. This run used 170 chunks, RRF constant 60, and full eligible-corpus branch rankings. [hybrid-results.json](hybrid-results.json) records corpus hashes, model revision, versions, and complete top-result evidence. [results.json](results.json) remains the historical two-mode run.

## Metrics

| Method | Hit@1 | Hit@3 | Unrelated returning results |
| --- | --- | --- | --- |
| keyword | 75% | 75% | 3/3 |
| semantic | 80% | 85% | 3/3 |
| hybrid | 75% | 75% | 3/3 |

## Per-query comparison

Ranks below are the first labeled answer in the top three; — is a top-three miss. Changes compare rank positions within the top three, treating all misses equally. Unrelated questions have no expected answer and are excluded from gain/regression counts.

| Question | Keyword | Semantic | Hybrid | vs keyword | vs semantic |
| --- | --- | --- | --- | --- | --- |
| What does a keyword retriever look for? | 1 | 1 | 1 | tie | tie |
| Why do neighboring text segments repeat some of their content? | — | 1 | — | tie | regression |
| How can related ideas be found when the wording is different? | 1 | 1 | 1 | tie | tie |
| What are the steps in the retrieval pipeline? | 1 | 1 | 1 | tie | tie |
| What do type hints help explain? | 1 | 1 | 1 | tie | tie |
| How many responsibilities should a function have? | 1 | 1 | 1 | tie | tie |
| Can I verify a retriever without an online service? | 1 | 1 | 1 | tie | tie |
| What acts as runnable examples of program behavior? | 1 | 1 | 1 | tie | tie |
| What was Li Jingsui originally called? | — | 3 | — | tie | regression |
| Who was Li Jingsui's mother? | 1 | 1 | 1 | tie | tie |
| Why did Xu Jingsui replace his brother as junior regent? | 1 | 1 | 1 | tie | tie |
| When did Xu Zhigao change his name to Li Bian? | 1 | 1 | 1 | tie | tie |
| Why did Li Jingsui choose the courtesy name Tuishen? | 1 | 1 | 1 | tie | tie |
| How did Li Jingsui react when Zhang Yi broke his jade cup? | 1 | 1 | 1 | tie | tie |
| How was Li Jingsui poisoned after playing polo? | 1 | 1 | 1 | tie | tie |
| What was Judy Garland's birth name? | — | — | — | tie | tie |
| Where was Judy Garland born? | — | 1 | — | tie | regression |
| Which role brought Judy Garland international recognition? | — | — | — | tie | tie |
| Which live album made Garland the first woman to win Album of the Year? | 1 | 1 | 1 | tie | tie |
| What song did Garland sing during her first appearance at age two? | 1 | — | 1 | tie | gain |
| How do I reset my email password? | — | — | — | n/a | n/a |
| What temperature should I bake sourdough bread at? | — | — | — | n/a | n/a |
| How do I replace a bicycle tire? | — | — | — | n/a | n/a |

## Result schema and interpretation

JSON `contents` describes its sections. Top-level metadata records model identity, versions, timestamp, corpus hashes, settings, and reproduction command. `results` contains labels, expected chunk identities, all three methods’ top-three passages/scores, and full first-answer ranks. Each hybrid result includes `keyword_rank` and `semantic_rank` in the full branch lists; null means absent. `changes` reports top-one and top-three gains/ties/regressions against each baseline. `metrics` excludes unrelated queries from the hit denominators.

RRF combines ranks, not score magnitudes. With full semantic rankings, every literal match receives two contributions; this can promote a weak keyword hit above relevant semantic-only evidence. No relevance threshold or automatic fallback exists. Unrelated questions still return neighbors. Hybrid remains opt-in whether or not these aggregate results improve.
