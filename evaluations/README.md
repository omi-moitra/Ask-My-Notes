# Retrieval evaluation

## Contents

- [Current three-mode comparison](#current-three-mode-comparison)
- [How to reproduce and read the artifacts](#how-to-reproduce-and-read-the-artifacts)
- [Historical two-mode run](#historical-two-mode-run)

## Current three-mode comparison

The unchanged 23 questions now compare keyword, semantic, and hybrid search over the same current corpus. The 20 answerable queries yielded Hit@1 / Hit@3 of **75% / 75%** for keyword, **80% / 85%** for semantic, and **75% / 75%** for hybrid. All methods returned passages for all three unrelated queries.

Hybrid tied keyword's top-three answer-rank outcomes. Relative to semantic it improved one question, regressed on three, and tied on sixteen. Fixed equal-weight RRF with full branch rankings can reward weak literal matches over stronger semantic-only evidence. It remains opt-in; these results do not justify replacing either standalone mode.

## How to reproduce and read the artifacts

Run `.venv-semantic/bin/python -m evaluations.run_retrieval` from the project root with the pinned model already cached. The runner uses offline loading and writes [hybrid-results.json](hybrid-results.json) and [hybrid-results.md](hybrid-results.md); it does not overwrite this README or historical `results.json`.

The new Markdown report contains per-query gains and regressions. Its JSON companion records corpus hashes, model/package versions, original labels, full first-answer ranks, and top-three passages and raw scores for every method. Hybrid entries include their keyword and semantic ranks so fusion contributions can be checked. JSON `contents` and `explanation` describe the schema without unsupported comment syntax.

The historical section below preserves the earlier two-method measurements and original reproduction instructions. That command now runs all three methods and writes the new filenames. Use [results.json](results.json) to inspect the preserved historical evidence; compare fresh methods on one snapshot rather than mixing runs when notes change.

## Historical two-mode run

23 fixed questions against the current local notes: 20 answerable and 3 unrelated. Labels were selected before running retrieval. Both methods use identical 120-word chunks with 20-word overlap. A hit requires a chunk containing a labeled evidence phrase, not merely the correct file. Repeated equivalent answers outside these phrases may be undercounted. This is a small diagnostic set, not a general benchmark.

Run `.venv-semantic/bin/python -m evaluations.run_retrieval` from the project root. The pinned model must already be cached; inference runs offline. Full passages, scores, labels, and corpus hashes are in `results.json`.

| Method | Hit@1 | Hit@3 | Unrelated queries returning passages |
| --- | --- | --- | --- |
| keyword | 75% | 75% | 3/3 |
| semantic | 80% | 85% | 3/3 |

Semantic retrieval has no abstention threshold. Similarity scores are not confidence probabilities. A dash below means no labeled answer appeared in the first three results.

| Question | Keyword answer rank | Semantic answer rank |
| --- | --- | --- |
| What does a keyword retriever look for? | 1 | 1 |
| Why do neighboring text segments repeat some of their content? | — | 1 |
| How can related ideas be found when the wording is different? | 1 | 1 |
| What are the steps in the retrieval pipeline? | 1 | 1 |
| What do type hints help explain? | 1 | 1 |
| How many responsibilities should a function have? | 1 | 1 |
| Can I verify a retriever without an online service? | 1 | 1 |
| What acts as runnable examples of program behavior? | 1 | 1 |
| What was Li Jingsui originally called? | — | 3 |
| Who was Li Jingsui's mother? | 1 | 1 |
| Why did Xu Jingsui replace his brother as junior regent? | 1 | 1 |
| When did Xu Zhigao change his name to Li Bian? | 1 | 1 |
| Why did Li Jingsui choose the courtesy name Tuishen? | 1 | 1 |
| How did Li Jingsui react when Zhang Yi broke his jade cup? | 1 | 1 |
| How was Li Jingsui poisoned after playing polo? | 1 | 1 |
| What was Judy Garland's birth name? | — | — |
| Where was Judy Garland born? | — | 1 |
| Which role brought Judy Garland international recognition? | — | — |
| Which live album made Garland the first woman to win Album of the Year? | 1 | 1 |
| What song did Garland sing during her first appearance at age two? | 1 | — |
| How do I reset my email password? | — | — |
| What temperature should I bake sourdough bread at? | — | — |
| How do I replace a bicycle tire? | — | — |
