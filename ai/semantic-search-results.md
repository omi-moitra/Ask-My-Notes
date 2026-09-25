# Semantic Search: Validation Results

Verified: 2026-09-22

## Contents

- [Setup](#setup)
- [Fixed corpus and labels](#fixed-corpus-and-labels)
- [Measured rankings](#measured-rankings)
- [Offline and compatibility checks](#offline-and-compatibility-checks)
- [Interpretation and limits](#interpretation-and-limits)

## Setup

The model is `sentence-transformers/all-MiniLM-L6-v2`, pinned to revision `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`. Inference ran on CPU with Python 3.14.3 on macOS-26.5.2-arm64-arm-64bit-Mach-O. Default chunk size was 120 words with overlap 20; each fixture note becomes one chunk.

| Package | Tested version |
| --- | --- |
| huggingface-hub | 0.36.2 |
| numpy | 2.5.3 |
| scikit-learn | 1.9.1 |
| scipy | 1.18.1 |
| sentence-transformers | 5.1.2 |
| tokenizers | 0.22.2 |
| torch | 2.14.0 |
| transformers | 4.57.6 |

Sentence Transformers is pinned in the optional `semantic` extra; this table records the transitive versions actually tested, not a cross-platform lockfile. Python 3.10 remains the declared minimum. The interpreter available for this run was 3.14.3; no Python 3.10 execution claim is made.

Reproduce from the project root (or substitute an existing environment with the semantic extra):

```bash
python3 -m venv .venv-semantic
.venv-semantic/bin/python -m pip install -e '.[dev,semantic]'
# Populate the pinned model cache deliberately before disabling networking.
.venv-semantic/bin/python -m src.cli search "finding information" --retriever semantic --limit 1
# These integration tests prohibit socket connections and DNS lookups themselves.
.venv-semantic/bin/python -m pytest -m integration -s -q
```

## Fixed corpus and labels

The six short English notes and six query labels were written in [semantic_cases.py](../tests/fixtures/semantic_cases.py) before either method was run. The expected sources are backup.md for file recovery and bread.md for dough expansion. The two paraphrases share no retained keyword terms with their expected passages. The astronomy and football queries have no relevant passage in the corpus.

Both retrievers received identical chunks. These cases are a small feature acceptance check, not a benchmark establishing performance on general questions.

## Measured rankings

Scores below are full-precision values captured from the test output. Rankings are listed in order, up to three results per method. A keyword score and a semantic score cannot be compared numerically.

**Exact: external drive restore lost data**

Expected source: `backup.md`.

| Method | Ranked source : score |
| --- | --- |
| keyword | `backup.md` : 3.5619310044637524 |
| semantic | `backup.md` : 0.7064874042514685; `retrieval.md` : 0.04345156025155436; `plants.md` : -0.018114423015344015 |

**Exact: yeast ferments sugar**

Expected source: `bread.md`.

| Method | Ranked source : score |
| --- | --- |
| keyword | `bread.md` : 2.0377007749380978 |
| semantic | `bread.md` : 0.6278216576014681; `plants.md` : 0.050435139080508125; `retrieval.md` : 0.0040214260126363 |

**Paraphrase: How can I recover deleted computer documents?**

Expected source: `backup.md`.

| Method | Ranked source : score |
| --- | --- |
| keyword | `retrieval.md` : 0.750920989498456; `sleep.md` : 0.750920989498456 |
| semantic | `backup.md` : 0.45746154451663235; `retrieval.md` : 0.21792325739505938; `plants.md` : 0.03155894664170054 |

**Paraphrase: Why does a loaf expand during baking?**

Expected source: `bread.md`.

| Method | Ranked source : score |
| --- | --- |
| keyword | `cycling.md` : 0.6248040303366552 |
| semantic | `bread.md` : 0.5971316446809386; `plants.md` : 0.09336394521789596; `cycling.md` : 0.06940037710553534 |

**Unrelated: What is the orbital period of Neptune?**

Expected source: none.

| Method | Ranked source : score |
| --- | --- |
| keyword | No results |
| semantic | `cycling.md` : 0.055217242220056514; `retrieval.md` : 0.017090100839293302; `bread.md` : 0.0143246794090699 |

**Unrelated: Who won the 1998 football World Cup?**

Expected source: none.

| Method | Ranked source : score |
| --- | --- |
| keyword | No results |
| semantic | `retrieval.md` : 0.10395507221678933; `backup.md` : 0.03796866140719864; `bread.md` : 0.03419345518440409 |

## Offline and compatibility checks

- The default suite passed **39 tests**, with **3 real-model tests deselected**, in both the original keyword-only environment and the separate semantic environment. The original environment contains no `sentence_transformers` package.
- The explicit integration run passed **3 tests**. It verified the labeled comparison, empty-cache offline failure, and actual CLI warm-cache success/empty-cache exit 1. DNS and socket connections were blocked and recorded; no network attempt occurred.
- All nine tests from the stop-word milestone remain included. Deterministic additions cover vector validation, index reuse, tie ordering, original text, model setup, truncation warnings, and operational failures.
- Optional dependencies passed `pip check`. The first model download needed network permission in this workspace; subsequent offline tests needed none.

## Interpretation and limits

Both exact matches ranked their expected passage first in both methods. Both paraphrases ranked their expected passage first in semantic mode; keyword search missed both expected passages. This exceeds the planned top-three paraphrase acceptance target without changing the predefined labels.

Unrelated queries still returned three semantic neighbors. There is no calibrated abstention threshold, so a returned passage is not proof of relevance. Negative scores can appear in top results when enough passages are requested. Semantic scores are cosine similarities, not answer-confidence probabilities.

Model token limits can truncate overlong passages or queries. The adapter warns before encoding and retains full original text for display, so displayed tails may not have contributed to similarity. Stop-word filtering applies only to keyword retrieval. Small score differences across hardware/library versions are possible; tests check real-model ranking, not exact stored decimals.


Teaching-material validation: all 26 complete tutorial examples produced their expected output. Both HTML decks passed JavaScript syntax and structural/navigation checks; embedded source excerpts match current files. No browser was available for visual inspection. The code and runtime checks above were executed independently of slide rendering.
