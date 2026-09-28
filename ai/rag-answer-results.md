# Local RAG Answers: Implementation and Validation

Verified: 2026-09-25. Implementation delivered; one generation-quality acceptance check remains failed.

## Contents

- [Delivered behavior](#delivered-behavior)
- [Runtime and model](#runtime-and-model)
- [Checks and outcomes](#checks-and-outcomes)
- [Offline verification](#offline-verification)
- [Answer quality](#answer-quality)
- [Resources and limitations](#resources-and-limitations)
- [Teaching verification](#teaching-verification)
- [Reproduction and references](#reproduction-and-references)

## Delivered behavior

`ask` now retrieves evidence, builds whole-passage bounded context, calls a local generator, validates structured claims/citations, and displays original supporting passages. It defaults to semantic retrieval; keyword and hybrid are explicit alternatives. `search` keeps its keyword default and earlier behavior. Hosted switching remains future work.

The generator uses fixed loopback HTTP, bypasses proxies, follows no redirects, rejects untested/cloud model identities, and verifies the installed manifest before sending the question. No implicit pull, automatic retry, repair call, or hosted fallback exists. Empty retrieval abstains without contacting the runtime. Model/runtime failures remain errors, not abstentions. Missing/malformed citations are rejected before printing an answer.

## Runtime and model

| Setting | Tested value |
| --- | --- |
| Machine | Apple M1, arm64, 8 GiB RAM |
| Python | 3.14.3; declared project minimum remains 3.10 |
| Runtime | Ollama 0.34.3 CLI, installed in ignored project cache |
| Runtime archive SHA-256 | `2c45865f94bce0d4d1d2567603dd2fdacaf375585220a175aa4800105193d36e` |
| Generation model | `qwen2.5:1.5b`, 1.54B parameters, Q4_K_M, Apache 2.0 |
| Manifest digest | `65ec06548149b04c096a120e4a6da9d4017ea809c91734ea5631e89f96ddc57b` |
| Model download | 986,061,892 bytes reported by Ollama |
| Model capacity / configured context | 32,768 / 16,384 tokens |
| Output / adapter deadline | 512 tokens / 120 seconds |
| Request policy | Temperature 0, seed 0, nonstreaming, keep_alive 0 |
| Context / question | 12,000 serialized evidence characters / 2,000 question characters |
| Embeddings | Existing pinned MiniLM revision and semantic dependencies; no change |

The model tag is convenient for setup, but the manifest digest is enforced because tags can change. The answer adapter uses Python's standard library; no new Python runtime dependency was added. The only supported generation model setting is the documented pinned model. Model weights/runtime are not committed.

## Checks and outcomes

- **122 deterministic cases pass** in both `.venv` and `.venv-semantic`; 9 real-model cases are deselected by default. New cases exercise context identity/budgets, strict responses, unknown citations, failures, loopback transport, proxy isolation, model preflight, and ask CLI behavior.
- **5 existing offline embedding integration cases pass**, with their original labels and external client connections/DNS prohibited.
- **3 of 4 local-generation integration cases pass; 1 fails.** Supported answers, unrelated-question abstention, and the real semantic `ask` CLI pass. The instruction-adjacent answer case returns insufficient evidence instead of the expected supported answer. The original expectation is retained.
- An actual keyword `ask "How does retrieval work?"` generated a cited answer from the user's notes. Synthetic fixtures also exercised the complete semantic path with `--retrieval-offline`.
- Historical retrieval results, labels, and the user's `documents/History.md` were preserved. No hosted API calls or charges were introduced.

A failed generation-quality case is an outstanding acceptance issue, not a passing or skipped check. The application is usable for learning and inspecting evidence, but this report does not claim all real-model acceptance checks pass.

## Offline verification

The Ollama server and its worker processes ran under the macOS [loopback-only profile](../tests/fixtures/ollama-local-only.sb) with `OLLAMA_NO_CLOUD=1`. The profile denies external networking and allows local IPC over loopback. The API endpoint remained 127.0.0.1:11434.

A probe under the same profile received an OS permission denial when connecting to external IP 1.1.1.1:443; a loopback connection succeeded. Real generation and evaluation then ran successfully against the restricted daemon. Python integration fixtures additionally reject every client connection/DNS request except the exact loopback endpoint. This covers the separate-runtime boundary that Python monkeypatching alone would miss.

Initial runtime/model downloads required internet access and were performed explicitly before isolation. A normal server started without the OS profile is not equivalent to this measured network restriction, even with cloud features disabled. No system-wide network setting was changed and no background service was installed.

## Answer quality

The unchanged eight-case synthetic evaluation produced 8 valid response structures, 7 matching expected statuses, no runtime errors, and evidence coverage for all 5 answerable questions. Manual review found **3 complete correct answers among 5 answerable cases**, plus one incomplete conflict answer and one false abstention. All 3 unanswerable cases abstained correctly.

See [raw results and exact evidence](../evaluations/local-answer-results.json), [readable results](../evaluations/local-answer-results.md), and [manual review](../evaluations/local-answer-review.md). Valid citations prove source membership, not correctness or completeness. In the conflict case, Cedar was cited while the equally available Maple passage was ignored.

General prompt clarifications did not fix these small-model limitations. Longer examples also increased latency without solving them, so the final prompt remains shorter. Labels were not changed and the failed integration expectation remains visible. This is development evidence, not an unseen benchmark or a guarantee for personal notes.

## Resources and limitations

A sampled Ollama worker RSS was 1,499,072 KiB (about 1.43 GiB), plus about 22.5 MiB for the server. This is a point-in-time observation, not peak whole-system use; Metal allocations/shared mappings and the Python embedding process have separate accounting. Runtime logs reported approximately 934.69 MiB Metal-mapped model weights and 448 MiB KV cache. They should not simply be added to RSS as independent allocations.

In the final evaluation, per-question pipeline times ranged from about 7.6 to 19.4 seconds. Timing includes retrieval and model startup, and varies with other applications and memory pressure. `keep_alive=0` releases weights after each answer, trading speed for available memory. Runtime plus retained download archive used about 644 MiB; generation assets about 940 MiB on disk. Free space dropped to roughly 3.4 GiB during the work; no larger model was downloaded and no personal files were removed.

This Mac is sufficient for the small local RAG learning workflow. It is not an assurance that large models will fit comfortably. The immediate practical constraint is free disk space; better answer quality is a separate model/evaluation concern. No hardware purchase is required to use the implemented workflow.

## Teaching verification

All six learning companions include generation versus retrieval, the two local models, injected generators, JSON/context bounds, provenance versus factual support, abstention versus errors, local setup, and the observed quality failures. There are 13 concepts and 27 Python chapters, with 32 concept slides and 27 Python slides.

All **30 runnable tutorial examples** matched documented output without calling a real generator. Static checks verified **315 displayed source lines**, **26 full-source snapshots**, slide counts, unique IDs, navigation metadata, JavaScript syntax, and Markdown contents links. `git diff --check` passed. Visual slide inspection was unavailable because no browser-control capability is present in the current session; static checks do not establish visual layout quality.

## Reproduction and references

Follow [README local setup](../README.md#local-model-setup) to start the runtime using its existing project cache. From the repository root:

```bash
.venv/bin/python -m pytest -q
.venv-semantic/bin/python -m pytest -q
.venv-semantic/bin/python -m pytest -m integration -q
# Expected to retain the documented small-model quality failure:
.venv-semantic/bin/python -m pytest -m generation_integration -q
.venv-semantic/bin/python -m evaluations.run_answers
.venv-semantic/bin/python -m src.cli ask "How does retrieval work?" --retrieval-offline
```

The adapter uses [Ollama chat's JSON-schema response format](https://docs.ollama.com/api/chat), [installed-model metadata](https://docs.ollama.com/api/tags), and [documented cloud disabling/local runtime settings](https://docs.ollama.com/faq). The [model page](https://ollama.com/library/qwen2.5:1.5b) records its size, quantization, and license. Runtime archive metadata came from the [official v0.34.3 release](https://github.com/ollama/ollama/releases/tag/v0.34.3).
