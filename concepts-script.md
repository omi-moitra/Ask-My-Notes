# Video script: Learning Ask My Notes, one concept at a time

**Format:** Student-led walkthrough with screen recordings and simple diagrams.  
**Estimated runtime:** 25–30 minutes at a conversational pace, including pauses.
**Delivery:** Curious, professional, and conversational. Read the narration aloud; visual directions and source cues are production notes.  
**Companion guide:** [concept.md](concept.md). Source cues refer to the same code snapshot as that guide.

## Contents

- [Opening — What am I actually learning here?](#opening--what-am-i-actually-learning-here)
- [How to use concept.md](#how-to-use-conceptmd)
- [1. Overlapping chunk boundaries](#1-overlapping-chunk-boundaries)
- [2. Corpus-dependent inverse document frequency](#2-corpus-dependent-inverse-document-frequency)
- [3. Balancing relevance, repetition, and passage length](#3-balancing-relevance-repetition-and-passage-length)
- [4. Tokenization and the limits of literal matching](#4-tokenization-and-the-limits-of-literal-matching)
- [5. Source provenance and citation stability](#5-source-provenance-and-citation-stability)
- [6. Pipeline contracts and the path toward RAG](#6-pipeline-contracts-and-the-path-toward-rag)
- [7. Index lifecycle, consistency, and scaling](#7-index-lifecycle-consistency-and-scaling)
- [8. Deterministic ranking and floating-point arithmetic](#8-deterministic-ranking-and-floating-point-arithmetic)
- [9. Validation and failure semantics across layers](#9-validation-and-failure-semantics-across-layers)
- [10. Testing correctness versus measuring retrieval quality](#10-testing-correctness-versus-measuring-retrieval-quality)
- [11. Embeddings, cosine similarity, and local model lifecycle](#11-embeddings-cosine-similarity-and-local-model-lifecycle)
- [12. Rank fusion and candidate depth](#12-rank-fusion-and-candidate-depth)
- [Closing — How I would keep learning](#closing--how-i-would-keep-learning)

## Opening — What am I actually learning here?

**On screen:** Project folder, followed by the title “Ask My Notes: From files to useful passages.” Show the command `python -m src.cli search "How does retrieval work?"`.

**Narration:**

“I’m learning this project for the first time, and the basic idea sounds straightforward: put some notes in a folder, ask a question, and get relevant passages back.

But once I look at the code, I start running into questions. How big should a passage be? What makes one result more relevant than another? And how do I know where a result came from?

That’s what this walkthrough is about. I’m going to work through the twelve concepts in `concept.md`, explain the parts that take a little extra thought, and use small examples to make them easier to follow.

One detail to establish first: keyword search is the default, while semantic and hybrid modes use the optional local model stack. All three return passages from our notes. Semantic mode uses an embedding model; generated answers remain future work.”

## How to use concept.md

**On screen:** Open [concept.md](concept.md). Highlight the contents, then “Where encountered,” “Why difficult,” and “How to solve it” in the first entry.

**Narration:**

“I’m treating `concept.md` as my study guide. Each entry tells me where a concept appears, why it can be confusing, and how to reason through it. It also includes exact source-line references, so I can move from an explanation to the implementation.

Those references describe the code at the time the guide was written. If the files change later, the line numbers may move.

The guide also separates existing behavior from proposed improvements. That matters while I’m learning: I want to understand what the program actually does before deciding how I might change it.

I’ll follow the guide’s order, starting with how a document becomes a set of searchable passages.”

## 1. Overlapping chunk boundaries

**Source cue:** [src/chunker.py:20–41](src/chunker.py#L20), [tests/test_chunker.py:14–24](tests/test_chunker.py#L14).

**On screen:** Animate the words `one two three four five six seven` into three windows:

```text
one two three four
              four five six seven
                            seven
```

**Narration:**

“A chunk is a smaller section of a document. Searching chunks lets the program return a useful passage instead of an entire file.

The part I need to slow down for is overlap. If the chunk size is four words and the overlap is one, I move forward three words each time. That movement is called the stride: chunk size minus overlap.

With these seven words, the first chunk is ‘one two three four.’ The next starts with ‘four,’ keeping one word of shared context. Then this implementation creates a third chunk containing only ‘seven.’

That last chunk surprised me. The previous chunk already contained it. But the loop keeps starting windows while there are words left, and the test explicitly expects this result.

Overlap can preserve context near a boundary, but it also duplicates content. Larger chunks give me more surrounding text; smaller chunks give me more focused passages. There’s a tradeoff to test with actual questions.

My first step is to trace a tiny example like this by hand. Then I check the validation rules: size must be positive, and overlap must be smaller than size. Otherwise, the window cannot advance properly.

Stopping after a chunk reaches the end would be a possible improvement if I wanted to remove redundant tails. That would be a deliberate behavior change, including a test update.”

## 2. Corpus-dependent inverse document frequency

**Source cue:** [src/search.py:46–61](src/search.py#L46).

**On screen:** Three chunk cards. Put `notes` on all three and `retrieval` on only one. Reveal:

```text
N = number of chunks
df(term) = number of chunks containing the term
idf(term) = log((1 + N) / (1 + df(term))) + 1
```

**Narration:**

“Next is inverse document frequency, or IDF. The name sounds intimidating, but the intuition helps: a word that appears everywhere gives me less information about which passage to choose. A rarer matching word can help distinguish a passage.

The corpus is the collection being searched. In this code, the units being counted are chunks. Even though the variable says ‘document frequency,’ it counts how many chunks contain a word.

If ‘retrieval’ appears ten times in one chunk, that still adds only one to its document frequency. We’re counting presence across chunks, not repetition within a chunk.

For our three-chunk example, a word in all three gets an IDF weight of one. A word in just one gets one plus the natural log of two, about one point six nine.

I don’t need to memorize the formula immediately. I need to understand what changes its inputs. Adding files changes the corpus. Changing overlap also changes the corpus, because it changes which chunks contain each word.

That connection is the tricky part: chunking affects ranking statistics. To compare two ranking experiments fairly, I need to keep track of the collection and chunk settings, and rebuild the statistics when those change.”

## 3. Balancing relevance, repetition, and passage length

**Source cue:** [src/search.py:72–92](src/search.py#L72).

**On screen:** Reveal the score in three steps: “Count matching terms, capped at 3” → “Multiply by rarity weight” → “Divide by square root of retained-token count.”

**Narration:**

“Now I can follow how those weights become a score.

For each matching query term, the program counts its occurrences in the chunk, caps that count at three, and multiplies by the term’s IDF weight. It adds those contributions, then divides by the square root of the chunk’s retained-token count.

Let me use a simple made-up weight of two. If a matching term appears twice, its contribution is four. If that passage contains sixteen tokens, the denominator is four, giving a score of one for this single-term example.

The repetition cap means typing the same word twenty times in a passage doesn’t keep increasing its contribution. Extra retained tokens still increase the length penalty, though.

Query repetition behaves differently: the query becomes a set of unique terms. Searching for ‘Python Python’ has the same effect as searching for ‘Python.’

What I find useful here is separating the three influences: matching terms, rarity, and length. When a result surprises me, I can inspect each one.

I also need to read the score correctly. A score of point eight does not mean an eighty-percent chance that the passage answers my question. It’s a ranking value from this particular formula. To judge whether the formula works well, I’ll eventually need examples of what should rank highly.”

## 4. Tokenization and the limits of literal matching

**Source cue:** [src/search.py:15–34](src/search.py#L15), [documents/History.md:5](documents/History.md#L5).

**On screen:** Display illustrative tokenizer outputs:

```text
"Python!"    → ["python"]
"documents"  → ["documents"]
"document"   → ["document"]
"note-taking" → ["note", "taking"]
"李景遂"      → []
```

**Narration:**

“Before any scoring happens, the program turns text into tokens: the pieces it will compare.

Here, it lowercases the text and extracts sequences of the letters a through z and digits zero through nine. That makes ‘Python’ and ‘python’ match, and punctuation acts as a separator.

But ‘document’ and ‘documents’ remain different tokens. The program doesn’t automatically connect related word forms or synonyms.

There’s a language limitation too. The history note contains Chinese characters, but this token pattern doesn’t capture them. If I search using only those characters, the query produces no tokens.

Another subtlety: the chunker splits on whitespace, while the retriever uses this token pattern. ‘Note-taking’ is one whitespace word but two search tokens. So the two stages don’t measure length in exactly the same way.

My debugging move is to inspect the tokens for both my query and the passage I expected to find. That tells me whether a match was possible before I investigate the scoring.

The stop-word filter is now implemented for both queries and passages. A tokenizer that supports more languages remains future work and would also require a rebuilt index.”

**Stop-word demonstration:** Run the README’s controlled comparison for query `how is retrieval`.

**Narration:** “A stop word is a word we deliberately leave out of matching. Our shared tokenizer excludes 26 words, including how, is, and the. THE theory is useful becomes theory and useful. We filter whole tokens, so theory survives. Python stores this vocabulary in a frozenset: an immutable set.

Before filtering, the passage how is how is how is scored 3.442672 and outranked the useful retrieval passage at 0.702733. Now the filler passage cannot match, and the retrieval passage comes first. The original text is still available for display.

We count only retained tokens in the length penalty, but all original chunks still count toward corpus size. A passage with no retained tokens is skipped before division. A query made entirely of stop words returns no results. We preserve no, not, and never, but literal matching still does not understand negation. This fixed English list has no override, so titles containing common words remain a limitation.”

## 5. Source provenance and citation stability

**Source cue:** [src/models.py:13–48](src/models.py#L13), [src/loader.py:30–35](src/loader.py#L30), [src/cli.py:91–95](src/cli.py#L91).

**On screen:** Follow a source label through `Document → DocumentChunk → SearchResult`. Show an illustrative label: `notes/example.txt (chunk 2)`.

**Narration:**

“Provenance means knowing where something came from. For a search result, that means being able to get back to the source passage.

The loader records the file’s path relative to the documents folder. The chunker carries that path forward and adds a chunk number. The search result keeps the chunk alongside its score, and the command line prints the source information.

That’s a helpful chain to follow through the code. The data records are frozen dataclasses, which prevent normal reassignment of their fields.

But I shouldn’t assume ‘chunk two’ is a permanent citation. If I add a paragraph near the beginning or change the chunk size, chunk two can contain different text.

The application also doesn’t store original line numbers. The source-code line references in `concept.md` are separate from the document references printed by the app.

For the current version, the filename and chunk number help me locate a result. For durable citations later, I’d want a document version and the passage’s original position, recorded before whitespace normalization removes that detail.”

## 6. Pipeline contracts and the path toward RAG

**Source cue:** [src/models.py:51–65](src/models.py#L51), [src/cli.py:58–95](src/cli.py#L58), [future extensions](PROJECT_OVERVIEW.md#future-extension-points).

**On screen:** Show `Load → Chunk → Retrieve → Print`. Add a dashed future branch from retrieved passages to “Generate an answer.”

**Narration:**

“At this point, I can see the whole pipeline. Loading creates documents. Chunking creates passages. Retrieval creates ranked results. The command-line interface prints them.

A contract describes what one component promises to another. Here, the retriever’s search method accepts a query and a result limit, then returns search results.

The semantic implementation now follows that shape, using a different matching algorithm while returning the same kind of result objects.

The command line now selects keyword, semantic, or hybrid retrieval. All return the same result objects, so the CLI can display passages without knowing how their scores were calculated.

Also, this base class raises NotImplementedError when its search method is called. It doesn’t prevent me from creating an instance in the first place.

RAG stands for retrieval-augmented generation. A future generation stage would use retrieved passages as context for an answer. That stage doesn’t exist here yet.

As a student, I find it easier to understand and test each stage separately, then follow the data between them. It gives me a clear place to look when something goes wrong.”

## 7. Index lifecycle, consistency, and scaling

**Source cue:** [src/search.py:46–61](src/search.py#L46), [src/search.py:78–92](src/search.py#L78), [src/cli.py:57–85](src/cli.py#L57).

**On screen:** Align two rows: `Chunk A | Chunk B` and `Counts A | Counts B`. Animate a hypothetical caller reversing only the chunk list, leaving the counts unchanged. Label “Potential mismatch.”

**Narration:**

“An index is prepared information that helps the search run. This retriever prepares term counts and rarity weights when it’s created.

The important idea is consistency: the chunks and the prepared statistics must describe the same collection at the same moment.

The keyword retriever stores the caller’s chunk list directly. The semantic retriever now protects its index by snapshotting the list into a tuple. If another part of a future application reordered that list afterward, the stored counts could become associated with the wrong chunks. The code pairs them by position using zip.

The current command-line flow creates the retriever and searches immediately, without making that kind of change. But if I reused this class in a longer-running service, I’d want to copy or freeze the collection and replace related index data together when it changes.

There’s a performance tradeoff too. Each command reloads and indexes the collection, and each search checks every chunk. That’s easy to follow for a small local project.

For a larger collection, an inverted index could map each term to the chunks containing it, helping us find candidates directly. Caching could avoid repeated setup, but then I’d need rules for refreshing it when files, tokenization, or chunk settings change.”

## 8. Deterministic ranking and floating-point arithmetic

**Source cue:** [src/loader.py:24–25](src/loader.py#L24), [src/search.py:73–102](src/search.py#L73).

**On screen:** Show the ordering rules: “Higher score first → Source filename → Chunk number.” Then show illustrative scores `0.81234` and `0.81231`, both displayed as `0.812`.

**Narration:**

“Deterministic behavior means I can repeat the same operation with the same inputs and get the same result. That makes debugging and comparing changes much easier.

This project sorts file paths during loading. It also sorts results by score, then uses filename and chunk number to resolve equal scores.

The subtle part happens before sorting. Matching terms are stored in a set, and their iteration order can vary between processes. Computers store floating-point values with limited precision, so changing the order of addition can slightly change the result.

I wouldn’t expect that to overturn clearly different scores, but it can matter when scores are extremely close. Tie-breakers only resolve equal scores; they don’t remove tiny differences created during calculation.

If I needed stricter reproducibility, I could sum terms in a fixed order and consider math.fsum for more accurate summation.

I also need to remember that the command line shows only three decimal places. Two displayed scores can look equal while their full values differ. When investigating ranking, I should inspect the actual values.”

## 9. Validation and failure semantics across layers

**Source cue:** [src/cli.py:27–35](src/cli.py#L27), [src/cli.py:58–89](src/cli.py#L58), [src/chunker.py:20–23](src/chunker.py#L20), [src/search.py:69–76](src/search.py#L69).

**On screen:** Three cards: “Invalid settings,” “Unable to load data,” and “Valid search, no matches.” Show current exit codes: no loaded documents → `1`; no matches → `0`.

**Narration:**

“I’m learning that ‘nothing came back’ can mean several different things.

Maybe the collection is empty. Maybe the query has no matches. Or maybe the settings are invalid and the program can’t complete the operation.

The command-line parser checks that chunk size is an integer, but a negative integer still passes that check. The chunker then rejects it because the value doesn’t make sense for a window size.

A non-positive result limit is treated differently: the search method intentionally returns an empty list.

The command line returns exit code one when no documents were loaded or an expected semantic dependency/model failure occurs. Invalid semantic-only options in keyword mode return two. A completed search returns zero, including when its result list is empty. Exit codes let a shell or another program distinguish success from a problem.

Some failures still escape as exceptions, including file-reading errors and invalid chunk settings. Also, the collection chunker validates through individual documents, so an empty collection never reaches those checks.

My approach is to define each case explicitly. What should the user see? What should a calling program receive? Future improvements could validate settings earlier and handle expected exceptions with clear messages. First, though, I need to understand the current choices rather than treating every empty result as the same condition.”

## 10. Testing correctness versus measuring retrieval quality

**Source cue:** [tests/test_loader.py:11–22](tests/test_loader.py#L11), [tests/test_chunker.py:14–31](tests/test_chunker.py#L14), [tests/test_search.py:21–41](tests/test_search.py#L21).

**On screen:** Show the test files beside the recorded six-query comparison in ai/semantic-search-results.md. Point out the expected source, keyword results, and semantic results for each query.

**Narration:**

“This concept connects implementation with evidence: how do I know this works?

The project has 60 deterministic tests and five explicit model checks, including stop-word filtering, empty-token safety, query equivalence, ties, and retained-token normalization. They check things like loading a nested file, preserving chunk metadata, rejecting invalid overlap, and ranking a matching passage above another result.

Those are useful, concrete examples of expected behavior. But retrieval quality asks another question: when someone asks a real question, does the program return useful evidence?

I need both kinds of checking. For correctness, I can use small cases where I understand the answer exactly. For quality, I need representative questions and passages I’ve labeled as relevant.

The keyword tests isolate empty and stop-word-only queries against populated indexes. Adding stop words does not change keyword results or scores. Semantic mode keeps those words and tests a different contract.

The fixed six-query comparison now records whether the expected passages appear near the top. Both predefined paraphrases ranked first in semantic mode and were missed by keyword search. A broader evaluation should also inspect duplication: three overlapping passages might contain almost the same information.

That would help me compare chunk sizes or scoring changes using evidence. The current suite checks selected behaviors; a broader retrieval evaluation is still future work.”

**Testing walkthrough:** Open `tests/test_hybrid.py` and read `test_worked_example_uses_order_not_scores`. Identify arranged rankings, the fusion call, and assertions. Then show `tests/test_semantic_integration.py`: it uses the real cached model. Explain that 60 default cases and five integration cases count parametrized inputs, not just functions. Run `.venv/bin/python -m pytest -v`; show how `PASSED`, `FAILED`, and `deselected` differ. For real-model checks use `.venv-semantic/bin/python -m pytest -m integration -v` with the cache prepared. Finally show `evaluations/hybrid-results.md`: passing correctness checks coexists with hybrid's 75% Hit@3 versus semantic's 85%. Ask the learner which evidence answers “does it work as specified?” and which answers “does it retrieve the right passage?”

## 11. Embeddings, cosine similarity, and local model lifecycle

**Source cue:** [src/semantic.py](src/semantic.py), [semantic tests](tests/test_semantic.py), and [comparison results](ai/semantic-search-results.md).

**On screen:** Show `[3, 4] → [0.6, 0.8]`; compare against `[1, 0]`. Reveal the dot product `0.6`. Open the two paraphrase rows in the measured comparison.

**Narration:** “The new semantic option turns each passage into a vector. We compare directions using cosine similarity. Dividing by vector length removes magnitude, so a normalized dot product is enough. The coordinates are learned features, not a list of human-readable meanings.

A fake encoder lets me test the arithmetic with tiny vectors: same direction is one, perpendicular is zero, opposite is minus one. It also lets me prove that passages are encoded once and their original sources are preserved. That requires no model download.

Then I need a real model check. Our two predefined paraphrases missed their expected passage with keyword search and ranked it first with semantic search. The unrelated questions also returned passages, which shows why similarity is not confidence and why nearest does not mean relevant.

The model is an optional dependency. Lazy loading means an empty request does not import it or download assets. Cached model files survive between commands, while passage vectors live only in memory. Offline mode loads a pinned local snapshot; our integration tests forbid network connections.

Semantic input keeps stop words and sentence context. The model can truncate long input at its token limit; we warn about that and retain original display text. This still returns passages, not generated answers.”

**Exercise:** If `[3, 4]` and `[30, 40]` point the same way, should their cosine differ? No. Normalization removes magnitude. Could a low-similarity passage still appear in the top three? Yes; no relevance threshold exists.

## 12. Rank fusion and candidate depth

**Source cue:** [src/hybrid.py](src/hybrid.py), [tests/test_hybrid.py](tests/test_hybrid.py), and [the measured evaluation](evaluations/hybrid-results.md).

**On screen:** Show keyword `[A, B]` and semantic `[C, A]`. Label positions 1 and 2, then reveal A's two contributions. Show the diagnostic metrics next to the counterexample.

**Narration:** “Hybrid search does not add a keyword score to a cosine. Their scales differ. We add reciprocal rank contributions instead. First place contributes one divided by sixty-one. Second contributes one divided by sixty-two. A appears in both lists, so it wins this example; then C; then B.

The helper deduplicates by filename and chunk number. Same text in different places remains distinct. A repeated entry within one branch gets no extra vote, and conflicting source text is an error.

Candidate depth matters. We ask each branch for its full list, then apply the final limit. That lets agreement below the output cutoff rise after fusion and makes smaller outputs prefixes of larger ones.

Agreement can also mislead. If irrelevant A has a keyword match and ranks second semantically, it gets two contributions. Relevant B may rank first semantically but have no literal match, getting only one. A can win even though B answers the question.

That happened in our evaluation: hybrid's top-three hit rate is seventy-five percent versus semantic's eighty-five. It recovers one semantic miss and loses three semantic hits. We did not tune labels or constants after seeing those results. It remains an explicit option, not a new default.”

**Ask:** If all raw branch scores change but their orders stay fixed, should hybrid order change? No. If the model fails after keyword finds results, should hybrid return those hits? No: report the model error rather than silently dropping a branch.

**Live command:** `.venv-semantic/bin/python -m src.cli search "finding information" --retriever hybrid --offline`. The existing pinned cache is reused. Show component ranks in `evaluations/hybrid-results.json` to explain results hidden by three-decimal display rounding.

## Closing — How I would keep learning

**On screen:** Return to [concept.md](concept.md), then show `Load → Chunk → Tokenize and index → Rank → Display sources`.

**Narration:**

“After working through these concepts, I can follow how one note becomes a ranked search result. I can also see why a small decision in one stage affects another: overlap changes the chunks, the chunks change the statistics, and the statistics change the ranking.

My next study session would start with one short document and one query. I’d write down the chunks, inspect the tokens, calculate a score, and follow the source information into the output.

Then I’d change one thing, predict what should happen, and compare my prediction with the code.

I’ll keep `concept.md` beside me as a reference. It gives me the explanation and the source locations, while these small experiments give me a way to check my understanding.”
