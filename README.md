# Ask My Notes

Ask My Notes is a local command-line RAG learning application. `search` returns ranked passages; `ask` uses a small local language model to write an answer with citations. Keyword search and the local HTTP adapter use only Python’s standard library. Semantic retrieval is an optional dependency. Local generation has no hosted API fees.

For project-wide purpose, architecture, AI development guidance, and the roadmap, read the [Global AI Specification](ai/global-spec.md).

## Contents

- [Project structure](#project-structure)
- [Install](#install)
- [Run a search](#run-a-search)
- [How retrieval works](#how-retrieval-works)
- [Semantic search](#semantic-search)
- [Hybrid search](#hybrid-search)
- [Ask with a local model](#ask-with-a-local-model)
- [Local model setup](#local-model-setup)
- [Run tests](#run-tests)
- [Next extension points](#next-extension-points)
- [Stop-word filtering](#stop-word-filtering)
- [Before-and-after comparison](#before-and-after-comparison)

## Project structure

```text
documents/       Sample Markdown and text notes
src/
	chunker.py     Split documents into overlapping word chunks
	cli.py         Command-line interface
	loader.py      Recursively load .md and .txt files
	models.py      Typed data objects and the Retriever interface
	search.py      Explainable keyword ranking
	semantic.py    Optional local embeddings and cosine ranking
	hybrid.py      Equal-weight reciprocal-rank fusion
	answering.py   Bounded context, grounded-answer validation, and citations
	local_generator.py  Local Ollama adapter with a pinned model
tests/           Automated tests for each core component
pyproject.toml   Packaging and test configuration
```

The `Retriever` interface is shared by keyword, semantic, and hybrid search. `DocumentChunk` already keeps the source filename and chunk number for citations in generated answers.

## Install

Python 3.10 or newer is required. Create a virtual environment and install the project with its development dependency:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

The base keyword application has no runtime dependencies outside the Python standard library. Semantic search requires the optional extra below.

## Run a search

Put `.txt` or `.md` files anywhere under `documents/`. The loader searches recursively. Then run:

```bash
python -m src.cli search "How does retrieval work?"
```

The command prints up to three ranked passages, each with a score, source filename, and chunk number. Useful options include `--limit`, `--chunk-size`, `--overlap`, `--documents`, and `--verbose`. For example:

```bash
python -m src.cli --documents my-notes --chunk-size 80 --overlap 15 search "testing Python"
```

## How retrieval works

1. The loader finds `.md` and `.txt` files recursively and records each path relative to the documents directory.
2. The chunker splits each file into word windows. With a chunk size of 120 and overlap of 20, the next window starts 100 words later, preserving context at boundaries.
3. The keyword retriever lowercases text and extracts alphanumeric terms, then removes the fixed stop-word vocabulary from both passages and queries. For each chunk, it adds the inverse-document-frequency-weighted count of query terms, limits repeated terms to avoid domination by one word, and normalizes by retained-token count.
4. Results are sorted by descending score and ties are made deterministic with source filename and chunk number.

The default mode uses literal keyword search: “retrieval” and “finding” are different terms. That limitation is useful for this milestone because every ranking decision is visible in `src/search.py`.

## Semantic search

Install the local model stack and select semantic mode explicitly:

```bash
python -m pip install -e '.[dev,semantic]'
python -m src.cli search "finding information" --retriever semantic
python -m src.cli search "finding information" --retriever keyword
python -m src.cli search "finding information" --retriever semantic --offline
```

In this workspace, `.venv` remains keyword-only and `.venv-semantic` contains the optional dependencies. Use `.venv-semantic/bin/python` for semantic commands unless you install the extra in another environment.

The first online semantic search downloads the pinned CPU model `sentence-transformers/all-MiniLM-L6-v2` to `.cache/ask-my-notes/models`. Override that location with `--model-cache PATH`. `--offline` loads that same revision from cached files without network access; an absent or incomplete cache fails with setup guidance. A warm cache alone does not prevent network checks in online mode. Cache assets are ignored by Git. Notes are encoded locally, and passage vectors are rebuilt in memory for each CLI invocation.

Semantic search preserves whole sentences, including stop words, for the model's tokenizer. Unit-length embeddings are compared by their dot product (cosine similarity). The result format and source metadata match keyword mode, but score scales differ and must not be merged. Scores are not confidence probabilities. The measured [six-query comparison](ai/semantic-search-results.md) recovered both keyword-missed paraphrases as the first semantic result.

Semantic mode always returns the nearest eligible passages up to the requested limit, even for unrelated questions or negative similarity scores. Blank queries, empty corpora, and nonpositive limits return no results without loading the model. Nonblank stop-word-only or punctuation-only queries are encoded normally. No relevance cutoff is applied.

The model normally accepts up to 256 word-piece tokens, which are not the same as whitespace words. Overlength inputs trigger a stderr warning before truncation; the displayed original passage can include a tail that did not affect its score. Chunking itself is unchanged.

`--model-cache` and `--offline` require `--retriever semantic` or `--retriever hybrid`; invalid combinations exit 2. Missing dependencies and expected model/cache failures exit 1 with guidance. A completed search exits 0, even with no results; no loaded documents retains exit 1. Use global `--verbose` before `search` for retriever/model/cache details.

## Hybrid search

Hybrid mode combines full keyword and semantic rankings using equal-weight reciprocal rank fusion (RRF). A passage contributes `1 / (60 + rank)` from each branch that returned it, with ranks starting at one. The final limit applies after fusion. Raw keyword and cosine scores are never added together.

```bash
.venv-semantic/bin/python -m src.cli search "finding information" --retriever hybrid --offline
```

Hybrid uses the existing semantic extra, pinned model, and cache options. `--offline` requires a populated cache; missing dependencies or model failures exit 1 without returning partial keyword results. Blank requests and nonpositive limits avoid both branch searches. A nonblank query with no keyword matches can still return semantic neighbors through normal fusion.

Chunk identity is `(source, chunk_number)`. Identical duplicate inputs collapse; conflicting text for one identity raises an error. Original passages are preserved. Exact fused ties use source and chunk number; changing the output limit does not change the candidate set. Verbose diagnostics report constant, corpus size, and branch result counts on stderr.

**Measured limitation:** on the unchanged 23-question diagnostic set, hybrid Hit@3 was **75%**, keyword **75%**, and semantic **85%**. Hybrid recovered one semantic miss but lost three semantic hits. Full rankings give weak literal matches a second contribution, which can demote strong semantic-only evidence. Hybrid remains opt-in and has no relevance threshold. See [the three-way evaluation](evaluations/hybrid-results.md) and [validation report](ai/hybrid-search-results.md).

RRF scores can round to the same three-decimal display value; ordering uses full precision. They are neither confidence probabilities nor comparable with standalone scores.

## Ask with a local model

Once the local runtime and model are installed, use this workspace's semantic environment:

```bash
.venv-semantic/bin/python -m src.cli ask "How does retrieval work?" --retrieval-offline
# The base environment works with keyword evidence and the same local generator.
.venv/bin/python -m src.cli ask "How does retrieval work?" --retriever keyword
```

`ask` defaults to semantic retrieval; `search` still defaults to keyword. If your activated `.venv` lacks the semantic extra, use `.venv-semantic/bin/python` or explicitly select keyword. `--retrieval-offline` requires the existing embedding cache and only controls embedding loading. Answer generation always uses installed local weights. Do not use `ask --offline`; that ambiguous option is rejected. Keyword evidence rejects embedding-cache/offline flags.

Answers contain claim citations such as `[S1]`, followed by original passage text, relative source filename, and chunk number. Only cited passages are listed. Labels apply to this request, not permanent document locations. The model must abstain when evidence is insufficient; the application also abstains without calling it when retrieval is empty. Invalid citations or malformed answers are errors, not successful answers or silent fallback.

Limits are 1–20 candidate passages (`--limit`, default 3), 2–12,000 serialized evidence characters (`--context-chars`, default 12,000), 2,000 question characters, 512 generated tokens, and a 120-second adapter deadline. Whole passages are kept in ranking order when they fit; oversized ones are omitted. A conservative UTF-8/token bound can reject long multibyte inputs even within the character limit. Reduce context/chunk size rather than silently truncating evidence. Valid completion/abstention exits 0, operational errors exit 1, and invalid CLI input exits 2.

**Quality limitation:** this small model can miss an answer beside instruction-like text and can select one of two conflicting notes. A valid citation is not proof that the answer is complete or correct. Inspect the sources. See the [fixed answer evaluation](evaluations/local-answer-results.md), [manual review](evaluations/local-answer-review.md), and [validation report](ai/rag-answer-results.md).

## Local model setup

The tested configuration is **Ollama 0.34.3 with `qwen2.5:1.5b`**, Q4_K_M quantization, Apache 2.0 model license. The model download is approximately 986 MB; the extracted runtime plus retained archive used about 644 MiB in this workspace. Initial setup needs internet access; inference does not. Hardware tested: Apple M1, 8 GiB RAM. There is limited free disk space on this machine; no larger model is required for learning the workflow.

Ollama is a separate process, not a Python package. The adapter needs no extra Python dependency. For a fresh machine, install the appropriate runtime using [Ollama’s macOS instructions](https://docs.ollama.com/macos), then start its command-line server with cloud disabled. This workspace already has a verified runtime in the ignored project cache. From the repository root, in a separate terminal:

```bash
# Keep this foreground process running; Ctrl-C stops it.
OLLAMA_NO_CLOUD=1 OLLAMA_HOST=127.0.0.1:11434 \
OLLAMA_MODELS="$PWD/.cache/ask-my-notes/ollama-models" \
OLLAMA_NUM_PARALLEL=1 OLLAMA_MAX_LOADED_MODELS=1 \
.cache/ask-my-notes/ollama-runtime/ollama serve
```

If port 11434 is already occupied by the runtime started during development, use that instance; do not start a second server. For a fresh setup, in another terminal, explicitly download the model once:

```bash
OLLAMA_HOST=127.0.0.1:11434 .cache/ask-my-notes/ollama-runtime/ollama pull qwen2.5:1.5b
```

For a system installation, replace `.cache/ask-my-notes/ollama-runtime/ollama` with `ollama` in these commands. Model storage is determined by the server's `OLLAMA_MODELS`, not the client shell. The generation model is separate from the MiniLM embedding cache. Keep both for semantic `ask`.

The adapter supports only `qwen2.5:1.5b`, configured by `ASK_NOTES_LOCAL_MODEL` (defaults to that exact name), and requires manifest digest `65ec06548149b04c096a120e4a6da9d4017ea809c91734ea5631e89f96ddc57b`. Changed or cloud-backed models are rejected before the question is sent. Missing models produce setup guidance; `ask` never downloads one. It connects only to `127.0.0.1:11434`, ignores proxy/`OLLAMA_HOST` redirection, follows no redirects, retries no generation requests, and releases model memory after each response. A request can still time out on a busy machine.

For stronger offline validation on macOS, start the same server with `sandbox-exec -f tests/fixtures/ollama-local-only.sb` immediately before the executable. This profile blocks external networking for the server and its children while permitting loopback. Pull assets before using that profile. Cloud disabling alone is not equivalent to OS-level network isolation. The [Ollama FAQ](https://docs.ollama.com/faq) documents local/cloud settings; the [model page](https://ollama.com/library/qwen2.5:1.5b) documents size and license. Hosted generation remains a [separate future feature](ai/hosted-generation-switch-spec.md).

## Run tests

```bash
# Default: deterministic tests, no model dependency or network required.
python -m pytest -q
# Explicit real-model checks: install semantic dependencies and warm cache first.
python -m pytest -m integration -s -q
# Explicit local answer checks: requires the installed Ollama model and cached embeddings.
.venv-semantic/bin/python -m pytest -m generation_integration -q
```

Current deterministic validation: **122 tests pass** in both Python environments; **5 offline embedding integration checks pass**. The separate generation checks include a known small-model quality failure; see [current results](ai/rag-answer-results.md). Missing prerequisites fail explicitly, not silently skip. Default pytest excludes both integration markers.


## Next extension points

The current boundaries leave room for reranking, PDF-specific loaders, optional hosted generation, broader evaluation, and a FastAPI adapter without putting those concerns into the CLI.

## Stop-word filtering

The completed [feature spec](ai/stop-word-filter-spec.md) defines this fixed vocabulary:

```text
a, an, and, are, as, at, be, by, does, for, from, how, in, is,
it, of, on, or, that, the, this, to, was, were, what, with
```

Filtering matches whole normalized tokens, so `theory` survives even though `the` is excluded. Negation words (`no`, `not`, `never`), numbers, and repeated meaningful tokens remain. Keeping negation does not make the retriever understand sentence meaning. Common words can matter in titles and phrases; this small English vocabulary has no configuration or per-query override.

Chunking and displayed passage text remain unchanged. Index counts and length normalization use only retained tokens, while the IDF corpus size still includes all chunks. Chunks without searchable terms are skipped before scoring, avoiding division by zero. Queries containing only stop words produce `No matching passages found.` with exit code 0 when documents are available.

## Before-and-after comparison

The following controlled corpus was run before and after implementation on 2026-09-22, using query `how is retrieval`:

| Source | Chunk | Original text | Before score (rank) | After score (rank) |
| --- | --- | --- | --- | --- |
| `filler.txt` | 1 | `how is how is how is` | 3.442672 (1) | No match |
| `retrieval.md` | 1 | `retrieval finds useful passages` | 0.702733 (2) | 0.702733 (1) |

Repeated common words previously pushed the filler passage above the useful passage. Filtering removes that false match. This demonstrates one improvement, not a guarantee for every query; scores can also change because normalization excludes stop words.

Reproduce the filtered result from the project root:

```bash
.venv/bin/python - <<'PYTHON'
from src.models import DocumentChunk
from src.search import KeywordRetriever

# These passages isolate common-word noise from a meaningful keyword match.
chunks = [
    DocumentChunk("filler.txt", 1, "how is how is how is"),
    DocumentChunk("retrieval.md", 1, "retrieval finds useful passages"),
]
for result in KeywordRetriever(chunks).search("how is retrieval"):
    print(result.chunk.source, f"{result.score:.6f}")
PYTHON
```
