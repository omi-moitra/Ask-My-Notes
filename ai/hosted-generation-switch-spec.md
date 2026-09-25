# Feature Spec: Switching Between Local and Hosted Generation

Status: Future milestone — not implemented; depends on local `ask`.
Created: 2026-09-23

## Contents

- [Purpose and prerequisites](#purpose-and-prerequisites)
- [In scope](#in-scope)
- [Out of scope](#out-of-scope)
- [Shared architecture](#shared-architecture)
- [Configuration and switching](#configuration-and-switching)
- [Data handling and costs](#data-handling-and-costs)
- [Failures and rollback](#failures-and-rollback)
- [Tests and comparison](#tests-and-comparison)
- [Documentation requirements](#documentation-requirements)
- [Definition of done](#definition-of-done)

## Purpose and prerequisites

Add a future, explicit option to use a hosted language model for answer generation while retaining local generation as the default. Both choices use a model: “hosted” means the model runs at an external provider; “local” means it runs on this machine. This spec interprets switching back to a model as switching back to a hosted API.

Implement [local grounded answers](rag-answer-spec.md) first. This document is a migration plan, not an instruction to create an API account, install a hosted client, or send notes now. Local and hosted implementations must satisfy the same answer/citation contract. Existing search and embedding behavior stay unchanged.

## In scope

- Add one hosted adapter behind the existing injectable `Generator` interface.
- Add explicit backend selection and separate local/hosted model settings.
- Preserve local as the default and allow returning to it without code changes.
- Document credentials, transmitted content, model costs, timeout, and output limits.
- Reuse context building, response validation, citation rendering, and abstention semantics.
- Test configuration isolation and compare both backends on fixed answer fixtures.

## Out of scope

- Selecting or purchasing a provider account during the local-generation milestone.
- Automatic local-to-hosted fallback, routing, load balancing, or multiple hosted providers.
- Moving note storage, retrieval, or embeddings to a hosted service.
- Uploading the whole collection, provider file stores, hosted search tools, or persistent conversations.
- Changing retrieval parameters or evaluation labels to improve one backend's reported results.

## Shared architecture

```text
Same retriever -> same context builder -> selected Generator
                                        | local adapter
                                        | hosted adapter
              -> same response validator -> same answer and citations
```

Provider SDK types must not enter shared answer models. Translate the common instructions, question, evidence, and response schema at the adapter boundary. If the provider cannot support the required schema or context/output bounds, fail configuration rather than quietly weakening validation.

Import the hosted client lazily and make it an optional dependency. A local command must not instantiate a hosted client, read its key, probe its endpoint, or require its package. Conversely, hosted generation must not require the local generation runtime; semantic retrieval may still require the separate embedding stack.

## Configuration and switching

Proposed interface, to be added only in this later milestone:

```bash
# Explicit local generation; this remains the default when --generator is omitted.
python -m src.cli ask "How does retrieval work?" --generator local --retrieval-offline
# Selected passages go to the configured hosted provider.
python -m src.cli ask "How does retrieval work?" --generator hosted --retrieval-offline
# Returning to local is a command change, not a code or index migration.
python -m src.cli ask "How does retrieval work?" --generator local --retrieval-offline
```

`--generator` selects where answers are generated. `--retriever` still selects keyword, semantic, or hybrid retrieval. `--retrieval-offline` only controls embedding loading; it does not make hosted generation offline. Reject an ambiguous `ask --offline` option. Commands that omit `--generator` must always remain local, even if hosted credentials are present.

Proposed environment settings are `ASK_NOTES_LOCAL_MODEL` and `ASK_NOTES_HOSTED_MODEL`. The local milestone must settle its configuration names first; reuse its local name instead of introducing a conflicting alias. No environment setting silently changes the default backend. Provider selection is fixed to one adapter for this milestone, not inferred from which keys happen to exist.

Before implementation, select a hosted provider and model, check current official documentation, and record the exact tested identifier, client version, structured-output support, token limits, timeout, retry policy, and pricing. Document the provider's actual credential environment variable once selected. Do not request keys in chat or commit them. Missing hosted configuration must fail only when hosted mode is explicitly selected.

Switching steps:

1. Verify the local `ask` path works and preserve its model/runtime configuration.
2. Install the optional hosted dependency and configure the chosen model and credential outside version control.
3. Review the expected input/output costs and which passage data will leave the machine.
4. Run an explicitly selected hosted check on synthetic notes.
5. Compare citation support, abstention, correctness, latency, and cost before choosing hosted mode for real questions.
6. Return to `--generator local` at any time. The local runtime/assets must still be installed; failures never trigger a hosted fallback.

## Data handling and costs

The hosted request contains grounding instructions, the question, and only the bounded selected passage text and metadata. It must not contain unrelated files, absolute local paths, environment contents, or credentials in the prompt. Do not request provider storage or retention features unnecessarily; verify and document the provider's actual retention behavior rather than promising zero retention without evidence.

Hosted API use may incur charges for input and output, including additional billed tokens where applicable. Document rates and date checked, an example cost calculation with explicit assumptions, and actual usage when returned. Do not assume a chat subscription covers API calls or that trial credits are available.

Use one request per question, no automatic retries or repair requests, a finite timeout, bounded context, and a generation output cap. These constrain individual requests; they are not a guaranteed account-wide spending cap. Distinguish application limits from provider budget alerts or enforced limits. Local mode must incur no hosted requests or charges.

## Failures and rollback

Handle missing credentials/dependencies, authentication errors, rate limits, quota errors, timeouts, connectivity, context limits, and malformed responses as operational failures with nonzero exit status. Never disguise a provider error as insufficient evidence. Redact sensitive details from exceptions and logs.

No backend fallback is permitted in either direction. A local failure stays local; a hosted failure remains visible. Preserve original notes, cached embeddings, local model assets, and historical reports so returning to local requires no reindexing or file conversion. Removing hosted credentials must not affect local operation or `search`.

## Tests and comparison

Default tests use fake adapters and make no API calls. Cover explicit selection, local default despite a populated hosted environment, dependency/credential isolation, common schema validation, identical supplied evidence, timeouts, errors, output bounds, redaction, and no fallback. Verify a hosted failure causes no local generation call and a local failure causes no hosted call.

Keep local generation tests and hosted tests independently selectable. Introduce a `hosted_generation_integration` marker excluded from default and local-only test runs. Hosted checks require deliberately configured credentials and synthetic notes; record unavailable prerequisites rather than counting them as successful checks.

Compare local and hosted generation against the same frozen answer fixture and context snapshots. Record provider/runtime versions, model identifiers, corpus/context hashes, parameters, answers, citations, abstentions, latency, usage, and dated estimated costs. Review factual support separately from schema validity. Save hosted comparison artifacts under new names; do not overwrite local baseline or existing retrieval reports. A hosted model need not win to validate switching; report regressions honestly.

## Documentation requirements

Every created or modified file must have an accurate TOC and extensive explanatory comments appropriate to its format. Python needs contents docstrings and explanations of adapter boundaries and failure behavior; Markdown needs navigable contents; HTML needs current navigation and presenter notes. JSON reports need `contents` and `explanation` fields plus a documented schema.

Update usage docs, global roadmap, decisions, and all six learning companions when implemented. Explain generator versus retriever selection, local versus hosted inference, API credentials versus chat subscriptions, costs, transmitted data, and rollback. Keep examples clearly marked as proposed until commands exist. Use fake adapters for runnable teaching examples and synchronize source snapshots and slide counts. Record validation and visual-inspection limitations in `ai/hosted-generation-switch-results.md`.

## Definition of done

- [ ] Complete the local grounded-answer milestone and preserve its baseline.
- [ ] Select and document the hosted provider/model, current costs, retention behavior, and configuration.
- [ ] Implement one optional hosted adapter with the shared answer/citation contract.
- [ ] Add explicit backend selection with local as the unchanged default.
- [ ] Preserve dependency, credential, and network isolation between backends.
- [ ] Verify bounded requests, failure behavior, redaction, and no automatic fallback.
- [ ] Pass existing and new deterministic tests without API calls.
- [ ] Pass independently selected local and hosted integration checks; report actual prerequisites/outcomes.
- [ ] Compare both generators on identical evidence and record quality, latency, and cost.
- [ ] Verify switching back to local with hosted credentials removed and no external inference traffic.
- [ ] Update documentation and all six learning companions, checking TOCs, comments, examples, and slides.
- [ ] Record validation and review the final diff before marking this spec implemented.
