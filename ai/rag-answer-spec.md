# Feature Spec: Grounded Answers with Citations

Status: Implementation delivered — deterministic/offline checks verified; generation-quality acceptance remains open.
Updated: 2026-09-25
Created: 2026-09-23

## Contents

- [Purpose and definitions](#purpose-and-definitions)
- [In scope](#in-scope)
- [Out of scope](#out-of-scope)
- [Provider and configuration](#provider-and-configuration)
- [CLI behavior](#cli-behavior)
- [Architecture and context](#architecture-and-context)
- [Generation and citations](#generation-and-citations)
- [Failures and diagnostics](#failures-and-diagnostics)
- [Tests and evaluation](#tests-and-evaluation)
- [Documentation requirements](#documentation-requirements)
- [Definition of done](#definition-of-done)

## Purpose and definitions

Complete the first end-to-end retrieval-augmented generation (RAG) workflow: retrieve passages from the notes, give those passages and a question to a language model, and print a supported answer with inspectable citations. Existing `search` continues to return passages without calling an answer model.

A **retriever** selects candidate evidence. A **generator** writes an answer using that evidence. **Grounding** means the answer's factual claims are supported by the supplied passages. A **citation** maps a claim to a passage actually supplied to the generator. **Abstention** means reporting insufficient evidence instead of inventing an answer. Valid citation identifiers establish provenance, not factual support: groundedness also needs evaluation.

Reranking is deferred. The current 23-question diagnostic gives semantic Hit@3 of 85% and hybrid 75%. This supports using semantic retrieval initially for `ask`; it does not prove answer accuracy or general superiority. The missing generation stage is the next milestone.

## In scope

- Add a single-question `ask` subcommand with semantic retrieval by default and explicit keyword/hybrid alternatives.
- Reuse existing ingestion, chunking, retrieval, source metadata, and local embedding cache.
- Introduce an injectable generator interface and one local Ollama generator adapter.
- Build bounded context, a grounding instruction, and a question; validate structured answers before displaying them.
- Render claim-level citations and a source list with original relative paths, chunk numbers, and supporting passage text.
- Handle insufficient evidence, configuration errors, provider errors, and malformed output distinctly.
- Add model-free tests, explicit local-model checks, an answer evaluation, and synchronized learning materials.

## Out of scope

- Reranking, retrieval tuning, new embedding models, or changing `search` defaults.
- Chat history, agents, tool execution, web search, streaming, or document editing.
- PDF ingestion, a web/API interface, persistent indexes, and vector databases.
- Hosted generation, API billing/credentials, multiple generation backends, model training, or automated answer repair loops. A future hosted option is scoped separately in [the hosted-switch specification](hosted-generation-switch-spec.md).
- Guarantees that prompt instructions prevent every hallucination or prompt injection.
- A similarity cutoff presented as a universal confidence threshold.

## Provider and configuration

**Selected:** local answer generation on the user's Mac. Both embeddings and answer generation run locally. Normal answering must not send questions, note passages, or their metadata to a remote service. No hosted API account or per-request API payment is required; local computation still uses memory, disk, electricity, and time.

**Selected runtime/model:** Ollama 0.34.3 with `qwen2.5:1.5b`, Q4_K_M, Apache 2.0; manifest `65ec06548149b04c096a120e4a6da9d4017ea809c91734ea5631e89f96ddc57b`. The 986 MB model was tested on this Apple M1 with 8 GiB RAM. Runtime/model setup, measured memory/latency, and official references are recorded in [implementation results](rag-answer-results.md). No larger model was downloaded.

The adapter enforces the model digest and uses 16,384 context tokens, 512 output tokens, and a 120-second deadline. `ASK_NOTES_LOCAL_MODEL` defaults to the supported tag and rejects other names. The only endpoint is 127.0.0.1:11434; proxies and redirects cannot change it. Python uses the standard library. Ollama is a separately started service with cloud features disabled. Tests also isolate the daemon at the OS network boundary.

Separate initial setup from inference. Downloading runtime/model assets can require internet access and substantial disk space. Document model size before setup. Normal `ask` must use installed assets and must not silently pull models, check for updates, enable cloud-backed models, or fall back to a hosted service. Missing assets produce setup guidance.

Keep generation dependencies optional and lazy. Keyword-only `search`, CLI help, and deterministic tests must remain usable without generation or semantic dependencies. A local service adapter, if selected, must use a fixed loopback endpoint with proxy bypass and redirects disabled; remote/custom hosts are out of scope. A local in-process adapter is also acceptable if its lifecycle and timeout are testable. Loopback communication is local networking, not a hosted API call.

Provide a single explicit generation-model configuration, named separately from the embedding model and cache. Validate availability and structured-output compatibility. An unavailable runtime, missing model, unsupported response mode, or insufficient memory must produce an actionable error, with no substitution to another model.

The injectable `Generator` boundary must remain independent of runtime details so a future hosted adapter can reuse context construction, answer validation, and citations. See [Switching to hosted generation](hosted-generation-switch-spec.md); that later spec does not authorize hosted calls in this milestone.

## CLI behavior

These commands are implemented; install/start the documented local runtime first:

```bash
# Semantic retrieval is the ask default; its dependencies are required.
python -m src.cli ask "How does retrieval work?" --retrieval-offline
# A keyword alternative avoids the embedding model, but still needs a generator.
python -m src.cli ask "How does retrieval work?" --retriever keyword
# Global ingestion settings stay before the subcommand.
python -m src.cli --documents documents ask "How does retrieval work?" --limit 3
```

`ask` accepts `--retriever keyword|semantic|hybrid` and a `--limit` from 1 through 20 (default 3). This limit controls candidate passages, not answer sentences. Keep existing global chunking and verbosity options. Preserve all `search` behavior and its keyword default.

For `ask`, use a clearly named `--retrieval-offline` flag with `--model-cache` for semantic/hybrid retrieval. Reject these flags in keyword mode. Answer generation always uses local, preinstalled assets. With semantic/hybrid retrieval, `--retrieval-offline` additionally prevents embedding-model downloads or network checks; without it, the existing embedding loader may access its model repository. Keyword retrieval needs no model download. Existing `search --offline` remains unchanged. Do not add an ambiguous `ask --offline` alias. Help must distinguish local generation from offline retrieval.

Reject blank questions, nonpositive limits, or invalid budgets as usage errors (exit 2). A missing/unreadable usable collection or failed retrieval/generation is an operational error (exit 1). A valid answer or a deliberate insufficient-evidence result exits 0. With no retrieved passages, return the insufficient-evidence result without contacting the generator.

## Architecture and context

```text
CLI -> loader -> chunker -> selected Retriever
    -> context builder -> Generator -> response validation -> answer + sources
```

Suggested responsibilities: `src/answering.py` owns context, answer types, orchestration, and validation; a separate provider adapter owns SDK/runtime concerns; `src/cli.py` owns configuration and rendering. Existing `Retriever.search` and `SearchResult` stay compatible. Supply a fake generator directly in tests, just as semantic tests supply fake encoders.

Context construction must be deterministic. Preserve ranking order; collapse repeated `(source, chunk_number)` identities only when text matches, and reject conflicting text. Keep equal text at different identities distinct. Assign request-local citation IDs `S1`, `S2`, and so on to the passages actually included. IDs and chunk numbers are not durable document identifiers.

Use a documented total context character budget (12,000 characters including serialized passage metadata). Include whole passages in rank order while they fit; skip oversized passages rather than silently truncating evidence. Record omissions in debug counts. If none fit, report a context-budget error without calling the generator. Enforce a 2,000-character question cap, 512-token generation budget, at most 6 claims, 1,000 characters per claim, and an 8,000-character response ceiling. Character limits are reproducible bounds, not exact model token counts; the adapter must handle model context-limit errors clearly.

Separate system instructions, the question, and serialized evidence. Treat passage text and filenames as untrusted data even when they contain instruction-like text or delimiter characters. Encode them safely in a structured evidence block. The generator must not execute commands or follow instructions found in notes. This separation reduces confusion but is not a security guarantee.

## Generation and citations

Instruct the generator to answer only from supplied evidence, cite each factual claim, and abstain when evidence is insufficient. Outside knowledge must not fill gaps. Explain contradictions or missing coverage rather than pretending the notes establish an answer. Keep the response concise.

Use a typed response shape: `status` is `answered` or `insufficient_evidence`; `claims` is a list of objects containing nonblank `text` and a list of citation IDs. An answered result needs at least one claim, each with at least one known citation ID. An insufficient-evidence result has an empty claims list and is rendered using a fixed application message: “I couldn't find enough information in your notes to answer that.”

Validate response types, status, nonempty claim text, citation membership, duplicates, and output bounds. Reject unknown IDs, malformed responses, or answered claims with no citations. Do not guess intended IDs or turn provider failures into abstention. No automatic retry/repair request in this milestone; one question makes at most one generation request.

Render citation labels from validated IDs, not model-written source paths. List only cited passages, in context order, retaining exact original text and metadata. A structurally valid citation can still point to irrelevant evidence: tests and evaluation must distinguish citation validity from claim support.

## Failures and diagnostics

Expected dependency, runtime-unavailable, missing-model, out-of-memory, timeout, loopback-connectivity, context-limit, and response-validation errors produce concise stderr messages and nonzero status. Never print a partial answer as a successful result. Configure an explicit finite timeout and disable implicit adapter/runtime client retries for reproducible request counts.

Verbose diagnostics may include retriever/model identifiers, candidate and included-passage counts, omitted-passage counts, context size, and elapsed retrieval/generation time. Do not log credentials, full prompts, questions, or note contents through provider debugging. Standard output contains the answer or abstention and cited sources; diagnostics stay on stderr.

## Tests and evaluation

Default tests use fake retrievers/generators and make no network calls. Cover:

- Existing search behavior and optional-dependency isolation.
- CLI defaults, explicit modes, flags, blank input, invalid budgets, and exit codes.
- Stable context order, identity rules, exact metadata/text, escaping, and whole-passage budget boundaries.
- No generator call for empty retrieval, setup errors, or unusable context; exactly one call for a valid request.
- Prompt separation, instructions to abstain, and instruction-like note text retained as data.
- Valid answers, abstention, unknown citations, missing citations, malformed types/status, oversized responses, and provider failures.
- Deterministic citation rendering, captured stdout/stderr, and redacted diagnostics.

Explicit local-generation checks are separate from default tests and from existing embedding integration checks. Use a marker such as `generation_integration`, excluded by default alongside `integration`. Use synthetic fixture notes and an installed local model. Verify a supported answer, an unrelated question, and an instruction-like passage. Record prerequisites and failures; do not count an unavailable runtime/model as a passed check. These checks incur no hosted API charges.

Test rejection of remote endpoints and cloud-backed model identifiers, absence of automatic pulls, finite timeout behavior, and no hosted fallback. For a loopback runtime, allow only its documented local connection while blocking external networking; a Python socket mock alone does not prove that a separate runtime process stays offline. Validate offline inference at the runtime/process boundary (for example with external networking disabled after setup) and record the method and outcome. Run the full semantic `ask` path with cached embeddings and `--retrieval-offline`. If external-network isolation cannot be verified, disclose the limitation instead of claiming a proved offline guarantee.

For answer evaluation, preserve all existing retrieval labels and historical artifacts. Create a separate answer fixture with expectations set before running: single-passage answers, multi-passage synthesis, unrelated questions, conflicting notes, missing facts, and instruction-like evidence. Save reports separately under `evaluations/` with model/configuration, corpus hashes, exact supplied evidence, validated answers, citations, latency, and usage when available; omit credentials.

Report retrieval coverage, factual correctness, claim support, citation validity, answerable-question abstentions, and unsupported answers on unanswerable questions separately. Review factual support manually against the cited text. Do not mistake a correctly formatted answer for a correct answer, or one successful refusal for universal abstention reliability. Record shortcomings without changing fixture labels to make the run pass.

## Documentation requirements

Every created or modified file needs an accurate TOC and extensive explanatory comments appropriate to its format. Python modules/tests need contents docstrings and explanations of boundaries, validation, and edge cases. Markdown needs navigable contents and substantive explanations. HTML needs slide navigation, comments, and presenter notes. Generated JSON needs `contents` and `explanation` metadata plus a documented schema because JSON cannot contain comments.

Update README, project overview, global spec, decision log, and all six learning companions: concepts guide/script/slides and Python for Dummies guide/script/slides. Teach retrieval versus generation, dependency injection, context budgets, citation validation versus factual support, abstention, and provider configuration. Explain the separate embedding and generation models, local runtime setup, resource costs, and the distinction between initial downloads and offline inference. Keep proposed commands labeled until implemented. Run teaching examples without paid API calls; synchronize source excerpts, counts, navigation, and full-source snapshots. Record any visual-inspection limitation.

Store implementation evidence in `ai/rag-answer-results.md`, including actual tested versions, commands, counts, live-check outcomes, and evaluation limits. Do not mark planned work complete merely because the spec exists.

## Definition of done

- [x] Select and document the local runtime, tested model/digest, hardware requirements, configuration, dependencies, and offline behavior.
- [x] Implement the generator boundary, bounded context, structured response validation, and citation rendering.
- [x] Add `ask`, preserving existing `search` behavior and optional-dependency isolation.
- [x] Handle abstention, invalid input, provider failures, and diagnostics as specified.
- [x] Pass all existing and new deterministic checks without network/model downloads.
- [x] Pass existing offline retrieval integration checks without altering their labels.
- [ ] Pass every local-generation quality expectation. Checks ran under verified external-network isolation: three pass, while the injection-adjacent supported answer still abstains. Preserve this failure for follow-up.
- [x] Run and review the separate grounded-answer evaluation, preserving historical artifacts.
- [x] Update project docs and all six learning companions with comments and TOCs.
- [x] Verify teaching outputs, links, slide navigation, JavaScript, and source snapshots; document visual limitations.
- [x] Review the implementation diff and record actual validation, retaining the outstanding quality gate rather than declaring full acceptance.
