# Python for Dummies — Presenter Script

Companion to [the guide](python-for-dummies.md) and [the HTML slideshow](python-for-dummies-slideshow.html).

**Audience:** first-time Python readers. **Format:** read-aloud narration with a code walkthrough. Allow roughly 45–60 minutes with the examples and exercises, or split the tutorial into several sessions. Slide numbers match guide chapters. This is a narration script, not an executable Python program.

**Teaching rhythm:** explain one idea → read the example → predict the output → reveal the output → ask the exercise question → connect to the project. Let the learner answer before showing a solution. Examples are run locally in Python; the HTML controls reveal prepared output.

**Presenter setup:** open the HTML file in a browser. Use Previous/Next or Left/Right arrow keys, Home/End for the first/last slide, N for speaker notes, and F for fullscreen when supported. The Notes button exposes the narration for the current slide. Use the Slide menu to jump to a topic, and expand Show expected output or Check your understanding as you teach. Print produces one slide per page. Terminal commands are for the live demonstration, not something the slideshow executes.

## Contents

- [Slide 1 — The program you are learning](#slide-1--the-program-you-are-learning)
- [Slide 2 — Files, modules, and imports](#slide-2--files-modules-and-imports)
- [Slide 3 — Indentation, comments, and docstrings](#slide-3--indentation-comments-and-docstrings)
- [Slide 4 — Names, values, and basic types](#slide-4--names-values-and-basic-types)
- [Slide 5 — Functions, arguments, and return values](#slide-5--functions-arguments-and-return-values)
- [Slide 6 — Type hints describe expected values](#slide-6--type-hints-describe-expected-values)
- [Slide 7 — Lists, tuples, sets, and dictionaries](#slide-7--lists-tuples-sets-and-dictionaries)
- [Slide 8 — Conditions and truthiness](#slide-8--conditions-and-truthiness)
- [Slide 9 — Loops, ranges, and unpacking](#slide-9--loops-ranges-and-unpacking)
- [Slide 10 — Strings, indexes, and slices](#slide-10--strings-indexes-and-slices)
- [Slide 11 — Classes, instances, and dataclasses](#slide-11--classes-instances-and-dataclasses)
- [Slide 12 — Methods, self, and inheritance](#slide-12--methods-self-and-inheritance)
- [Slide 13 — Paths and reading files](#slide-13--paths-and-reading-files)
- [Slide 14 — Regular expressions and tokens](#slide-14--regular-expressions-and-tokens)
- [Slide 15 — Counting words with Counter](#slide-15--counting-words-with-counter)
- [Slide 16 — Comprehensions and generators](#slide-16--comprehensions-and-generators)
- [Slide 17 — Arithmetic and the search score](#slide-17--arithmetic-and-the-search-score)
- [Slide 18 — Sorting, lambdas, and result limits](#slide-18--sorting-lambdas-and-result-limits)
- [Slide 19 — Command-line arguments and execution](#slide-19--command-line-arguments-and-execution)
- [Slide 20 — Printing, formatting, and logging](#slide-20--printing-formatting-and-logging)
- [Slide 21 — Exceptions and context managers](#slide-21--exceptions-and-context-managers)
- [Slide 22 — Tests, fixtures, and assertions](#slide-22--tests-fixtures-and-assertions)
- [Slide 23 — Running and tracing the project](#slide-23--running-and-tracing-the-project)
- [Slide 24 — Stop-word filtering with frozenset](#slide-24--stop-word-filtering-with-frozenset)
- [Slide 25 — Semantic search, vectors, and optional dependencies](#slide-25--semantic-search-vectors-and-optional-dependencies)
- [Slide 26 — Hybrid search with reciprocal ranks](#slide-26--hybrid-search-with-reciprocal-ranks)

- [Slide 27 — Local answers, JSON, and generator protocols](#slide-27--local-answers-json-and-generator-protocols)

## Slide 1 — The program you are learning

**Goal:** Read local notes.

**Explain:**

We will learn Python by following one note through this program. First we read the note, then split it, then rank its passages against a question. Each step introduces a small piece of Python. You do not need to memorize the whole program. Keep asking: what value goes in, what happens to it, and what value comes out?

**Show the example — Search a tiny note:**

```python
from src.models import DocumentChunk
from src.search import KeywordRetriever

chunk = DocumentChunk("note.txt", 1, "Python makes notes searchable")
results = KeywordRetriever([chunk]).search("python")
print(results[0].chunk.source)
```

**Ask before revealing:** “What do you think this will print?” Pause while the learner reads the code. Then expand **Show expected output** on the slide.

```text
note.txt
```

**Explain the example, one step at a time:**

1. `DocumentChunk(...)` creates one searchable passage. Its three arguments are the filename, chunk number, and text.
2. `[chunk]` puts that passage in a list. `KeywordRetriever([chunk])` prepares the list for searching.
3. `.search("python")` returns matching results. `[0]` selects the first result.
4. `result.chunk.source` follows the result to its passage and then its filename. `print(...)` displays it.

**Practice question:** What does the search return: a passage or a generated answer?

**Answer to explain after the pause:** A matching passage with its source and score.

**Connect to the project:** Open guide chapter 1, under **In this project**, and find the same idea in src/cli.py · main. Explain how the small example relates to that code.

**Transition:** Next, we will look at files, modules, and imports.


## Slide 2 — Files, modules, and imports

**Goal:** A .py file is a module.

**Explain:**

Think of modules as labeled drawers. Import opens access to a tool in another drawer. Math stays under its module name; Path is imported directly. The dot before models says to look within this package. That is why our command uses python dash m src dot cli: it tells Python which package the module belongs to.

**Show the example — Import a function:**

```python
from src.search import tokenize

print(tokenize("Hello Python!"))
```

**Ask before revealing:** “What do you think this will print?” Pause while the learner reads the code. Then expand **Show expected output** on the slide.

```text
['hello', 'python']
```

**Explain the example, one step at a time:**

1. `from src.search import tokenize` makes the project’s tokenize function available by name.
2. `tokenize("Hello Python!")` passes text to that function.
3. The function returns a list of lowercase words. `print(...)` displays that returned list.

**Practice question:** What does the dot in from .models import Document mean?

**Answer to explain after the pause:** Look for models inside the current package.

**Connect to the project:** Open guide chapter 2, under **In this project**, and find the same idea in src/__init__.py · imports across src/ and tests/. Explain how the small example relates to that code.

**Transition:** Next, we will look at indentation, comments, and docstrings.


## Slide 3 — Indentation, comments, and docstrings

**Goal:** A colon starts a block.

**Explain:**

Look at the left edge of the code. The spaces tell you what is inside what. The error is inside the condition, and the condition is inside the function. The hash comment explains a decision to people. The triple-quoted docstring describes the function to people and Python tools. When a call spans several lines, its parentheses keep it together.

**Show the example — Read an indented block:**

```python
size = 4
# Only print when the size is positive.
if size > 0:
    print("Ready")
```

**Ask before revealing:** “What do you think this will print?” Pause while the learner reads the code. Then expand **Show expected output** on the slide.

```text
Ready
```

**Explain the example, one step at a time:**

1. `size = 4` stores the number 4 under the name size.
2. `#` introduces a comment. Python does not execute the comment.
3. `if size > 0:` asks whether size is greater than zero. The colon begins its block.
4. The indented `print` runs because the condition is true. Remove the indentation and it no longer belongs to the condition.

**Practice question:** What happens if size becomes 0?

**Answer to explain after the pause:** The condition is false, so the indented print statement does not run.

**Connect to the project:** Open guide chapter 3, under **In this project**, and find the same idea in src/chunker.py · chunk_document. Explain how the small example relates to that code.

**Transition:** Next, we will look at names, values, and basic types.


## Slide 4 — Names, values, and basic types

**Goal:** = assigns; == compares.

**Explain:**

An equals sign gives a value a name. Two equals signs ask whether values are equal. Here step becomes one hundred because one hundred twenty minus twenty is one hundred. Dot text reads an attribute; dot split followed by parentheses runs a method. Names can refer to the same object, so assigning a list to another name does not make a new list.

**Show the example — Assign a value:**

```python
chunk_size = 120
overlap = 20
step = chunk_size - overlap
print(step)
print(step == 100)
```

**Ask before revealing:** “What do you think this will print?” Pause while the learner reads the code. Then expand **Show expected output** on the slide.

```text
100
True
```

**Explain the example, one step at a time:**

1. The first two assignments name the window size and overlap.
2. `chunk_size - overlap` subtracts 20 from 120. The result is assigned to step.
3. `print(step)` displays 100.
4. `step == 100` compares two values. Its result is the Boolean value True.

**Practice question:** Which symbol assigns a value: = or ==?

**Answer to explain after the pause:** = assigns. == compares values.

**Connect to the project:** Open guide chapter 4, under **In this project**, and find the same idea in src/chunker.py · src/models.py · src/cli.py. Explain how the small example relates to that code.

**Transition:** Next, we will look at functions, arguments, and return values.


## Slide 5 — Functions, arguments, and return values

**Goal:** def defines reusable work.

**Explain:**

A function is a reusable recipe. Its definition lists the ingredients it accepts. The caller can use the default portion sizes or name replacements, as we do with chunk size four and overlap one. Return hands the finished result back. Notice that defining the recipe and actually cooking it are separate operations.

**Show the example — Call a function:**

```python
def advance(size, overlap=1):
    return size - overlap

print(advance(4))
print(advance(4, overlap=2))
```

**Ask before revealing:** “What do you think this will print?” Pause while the learner reads the code. Then expand **Show expected output** on the slide.

```text
3
2
```

**Explain the example, one step at a time:**

1. `def advance(size, overlap=1):` defines a function with two parameters. The second has a default.
2. `return size - overlap` calculates a value and sends it back to the caller.
3. `advance(4)` uses the default overlap of 1, so it returns 3.
4. `advance(4, overlap=2)` replaces the default, so it returns 2. This small teaching function illustrates the subtraction used by the chunker.

**Practice question:** Which overlap value is used by advance(4)?

**Answer to explain after the pause:** The default value, 1.

**Connect to the project:** Open guide chapter 5, under **In this project**, and find the same idea in src/chunker.py · chunk_document and chunk_documents. Explain how the small example relates to that code.

**Transition:** Next, we will look at type hints describe expected values.


## Slide 6 — Type hints describe expected values

**Goal:** name: Type describes a value.

**Explain:**

Read the colon as “is expected to be,” and the arrow as “returns.” Tokenize expects text and returns a list of strings. These labels help readers and development tools. They do not stop someone from passing the wrong thing. Actual validation is performed by the if statements that raise errors.

**Show the example — Read a type hint:**

```python
def label(text: str) -> str:
    return text

print(label("notes"))
print(label(42))
```

**Ask before revealing:** “What do you think this will print?” Pause while the learner reads the code. Then expand **Show expected output** on the slide.

```text
notes
42
```

**Explain the example, one step at a time:**

1. `text: str` describes the expected input type. `-> str` describes the expected return type.
2. `return text` gives back exactly what was passed in.
3. The first call passes a string. The second deliberately passes an integer.
4. Both run because annotations do not insert runtime checks. The second call violates the hint, which a type checker can flag.

**Practice question:** Why does label(42) still run?

**Answer to explain after the pause:** Type hints describe expected types. This function has no runtime type check.

**Connect to the project:** Open guide chapter 6, under **In this project**, and find the same idea in src/models.py · src/chunker.py · src/search.py. Explain how the small example relates to that code.

**Transition:** Next, we will look at lists, tuples, sets, and dictionaries.


## Slide 7 — Lists, tuples, sets, and dictionaries

**Goal:** Lists preserve order and allow repeats.

**Explain:**

Choose a collection based on what the data means. Chunks belong in a list because order matters. Query words belong in a set because duplicates should count once. A dictionary pairs each word with its weight. A tuple groups the sorting priorities. Also watch append versus extend: one adds a single object, while the other adds the contents of a collection.

**Show the example — Choose a collection:**

```python
words = ["python", "python", "notes"]
unique_words = set(words)
weights = {"python": 2.0}
print(len(words))
print(len(unique_words))
print(weights["python"])
```

**Ask before revealing:** “What do you think this will print?” Pause while the learner reads the code. Then expand **Show expected output** on the slide.

```text
3
2
2.0
```

**Explain the example, one step at a time:**

1. The list words contains three entries, including a repeated word.
2. `set(words)` produces unique entries: python and notes.
3. `{"python": 2.0}` creates a dictionary linking the key python to a number.
4. `len(...)` counts entries. `weights["python"]` retrieves the value stored under that key.

**Practice question:** Why does unique_words contain only two items?

**Answer to explain after the pause:** A set stores each distinct value once.

**Connect to the project:** Open guide chapter 7, under **In this project**, and find the same idea in src/loader.py · src/search.py · tests/test_loader.py. Explain how the small example relates to that code.

**Transition:** Next, we will look at conditions and truthiness.


## Slide 8 — Conditions and truthiness

**Goal:** if runs a block only when its condition is true.

**Explain:**

Conditions are gates. The loader skips an entry if it is not a file or its extension is unsupported. Empty collections behave like false, so “if not results” means there were no results. A string containing spaces is still nonempty; strip removes those spaces for the check. Finally, the short inline if expression chooses a logging level.

**Show the example — Check for empty text:**

```python
text = "   "
print(bool(text))
print(bool(text.strip()))
```

**Ask before revealing:** “What do you think this will print?” Pause while the learner reads the code. Then expand **Show expected output** on the slide.

```text
True
False
```

**Explain the example, one step at a time:**

1. `text` contains three spaces, so it is a nonempty string.
2. `bool(text)` asks for its truth value and returns True.
3. `text.strip()` returns a new string with surrounding whitespace removed.
4. That new string is empty, so converting it to bool returns False. The original text is unchanged.

**Practice question:** Is a string containing three spaces empty?

**Answer to explain after the pause:** No. It is nonempty until strip removes the spaces.

**Connect to the project:** Open guide chapter 8, under **In this project**, and find the same idea in src/loader.py · src/chunker.py · src/cli.py. Explain how the small example relates to that code.

**Transition:** Next, we will look at loops, ranges, and unpacking.


## Slide 9 — Loops, ranges, and unpacking

**Goal:** for visits items from an iterable.

**Explain:**

The chunker needs two numbers: where to start reading and what chunk number to show a person. Range supplies positions zero, three, six in our small example. Enumerate attaches labels one, two, three. Two names on the left unpack each pair. Later, zip pairs each chunk with its counts so the search loop can use both together.

**Show the example — Number a loop:**

```python
for number, start in enumerate(range(0, 7, 3), start=1):
    print(number, start)
```

**Ask before revealing:** “What do you think this will print?” Pause while the learner reads the code. Then expand **Show expected output** on the slide.

```text
1 0
2 3
3 6
```

**Explain the example, one step at a time:**

1. `range(0, 7, 3)` supplies the positions 0, 3, and 6.
2. `enumerate(..., start=1)` pairs those positions with the numbers 1, 2, and 3.
3. `number, start` unpacks each pair into two names.
4. The indented print runs once per pair and displays both values separated by a space.

**Practice question:** Why is there no start position 7?

**Answer to explain after the pause:** range excludes its stop value. With a step of 3, the positions here are 0, 3, and 6.

**Connect to the project:** Open guide chapter 9, under **In this project**, and find the same idea in src/chunker.py · src/search.py · src/cli.py. Explain how the small example relates to that code.

**Transition:** Next, we will look at strings, indexes, and slices.


## Slide 10 — Strings, indexes, and slices

**Goal:** Indexes start at zero.

**Explain:**

Count positions from zero. A slice includes the start and stops just before the end. With a window of four and an overlap of one, starts move by three. That creates the first four words, then words four through seven, then a final chunk containing seven alone. This last chunk is easy to overlook, and the project has a test that confirms it.

**Show the example — Slice a list:**

```python
words = "one two three four five six seven".split()
for start in range(0, len(words), 3):
    print(" ".join(words[start:start + 4]))
```

**Ask before revealing:** “What do you think this will print?” Pause while the learner reads the code. Then expand **Show expected output** on the slide.

```text
one two three four
four five six seven
seven
```

**Explain the example, one step at a time:**

1. `.split()` changes a sentence into a list of seven words.
2. The range supplies starting positions 0, 3, and 6.
3. `words[start:start + 4]` selects up to four words. Its stop position is excluded.
4. `" ".join(...)` combines the selected words with spaces. At start 6, only the word seven remains.

**Practice question:** How many chunks does this example produce?

**Answer to explain after the pause:** Three, including the final one-word chunk.

**Connect to the project:** Open guide chapter 10, under **In this project**, and find the same idea in src/chunker.py · tests/test_chunker.py. Explain how the small example relates to that code.

**Transition:** Next, we will look at classes, instances, and dataclasses.


## Slide 11 — Classes, instances, and dataclasses

**Goal:** A class defines a kind of object.

**Explain:**

A class defines a kind of record, and an instance is one particular record. Document says every document has a source and text. Dataclass writes the repetitive record code for us. Frozen means we cannot normally replace a field after creation. A SearchResult contains a DocumentChunk, so result dot chunk dot source follows the objects to the filename.

**Show the example — Create a document:**

```python
from src.models import Document

note = Document(source="note.txt", text="Hello")
print(note.source)
print(note.text)
```

**Ask before revealing:** “What do you think this will print?” Pause while the learner reads the code. Then expand **Show expected output** on the slide.

```text
note.txt
Hello
```

**Explain the example, one step at a time:**

1. The import brings in the project’s Document class.
2. `Document(...)` creates one instance, with source and text supplied by name.
3. `note.source` reads the instance’s source field.
4. `note.text` reads its text field. The two print calls show these values on separate lines.

**Practice question:** What is note: a class or an instance?

**Answer to explain after the pause:** An instance of the Document class.

**Connect to the project:** Open guide chapter 11, under **In this project**, and find the same idea in src/models.py · Document, DocumentChunk, SearchResult. Explain how the small example relates to that code.

**Transition:** Next, we will look at methods, self, and inheritance.


## Slide 12 — Methods, self, and inheritance

**Goal:** A method is a function attached to a class.

**Explain:**

The retriever is more than a record: it remembers an index and performs searches. Self means this particular retriever. The keyword initializer saves its chunks and builds counts. The semantic retriever snapshots chunks and postpones encoding until an actual search. The parent class describes the search operation, and the subclass supplies its implementation. The parent is only a convention here; Python does not prevent creating it, but its search method raises an error.

**Show the example — Use an instance method:**

```python
from src.models import DocumentChunk
from src.search import KeywordRetriever

retriever = KeywordRetriever([DocumentChunk("a.txt", 1, "python")])
print(len(retriever.chunks))
print(len(retriever.search("python")))
```

**Ask before revealing:** “What do you think this will print?” Pause while the learner reads the code. Then expand **Show expected output** on the slide.

```text
1
1
```

**Explain the example, one step at a time:**

1. `DocumentChunk(...)` creates a passage and square brackets put it in a list.
2. `KeywordRetriever(...)` initializes an instance with that list.
3. `retriever.chunks` accesses the list stored on the instance; its length is 1.
4. `retriever.search("python")` calls a method on that same instance. Python supplies self, and the search returns one match.

**Practice question:** Do you pass self when calling retriever.search("python")?

**Answer to explain after the pause:** No. Python supplies the instance automatically.

**Connect to the project:** Open guide chapter 12, under **In this project**, and find the same idea in src/models.py · Retriever; src/search.py · KeywordRetriever. Explain how the small example relates to that code.

**Transition:** Next, we will look at paths and reading files.


## Slide 13 — Paths and reading files

**Goal:** Path represents a filesystem path.

**Explain:**

Path gives us operations for filenames and directories. The loader recursively finds entries and sorts them, then filters for supported files. Read text turns UTF-8 bytes into a Python string. The stored source is relative to the collection folder, making printed filenames easier to move between computers. The slash in the tests joins paths rather than dividing numbers.

**Show the example — Work with a path:**

```python
from pathlib import Path

path = Path("documents") / "note.md"
print(path.suffix)
print(path.relative_to("documents").as_posix())
```

**Ask before revealing:** “What do you think this will print?” Pause while the learner reads the code. Then expand **Show expected output** on the slide.

```text
.md
note.md
```

**Explain the example, one step at a time:**

1. `Path("documents")` represents a directory path.
2. For Path objects, `/ "note.md"` joins a filename to that path.
3. `.suffix` reads the extension, including the leading dot.
4. `.relative_to("documents")` removes the directory prefix; `.as_posix()` turns the remaining path into text with forward slashes.

**Practice question:** Does constructing this Path create the file?

**Answer to explain after the pause:** No. A Path represents a location. Creating or writing a file is a separate operation.

**Connect to the project:** Open guide chapter 13, under **In this project**, and find the same idea in src/loader.py · load_documents. Explain how the small example relates to that code.

**Transition:** Next, we will look at regular expressions and tokens.


## Slide 14 — Regular expressions and tokens

**Goal:** re.compile prepares a pattern.

**Explain:**

Tokenization decides what counts as a search word. The pattern means one or more lowercase ASCII letters or digits. Lowercasing makes Python and python match. A decimal point separates three and ten into different tokens. This is literal matching: related words do not automatically match, and accented letters are outside this pattern.

**Show the example — Split text into tokens:**

```python
from src.search import tokenize

print(tokenize("Python 3.10!"))
print(tokenize("Python_3!"))
```

**Ask before revealing:** “What do you think this will print?” Pause while the learner reads the code. Then expand **Show expected output** on the slide.

```text
['python', '3', '10']
['python', '3']
```

**Explain the example, one step at a time:**

1. Import the project’s tokenize function so you can try its actual behavior.
2. The function lowercases Python before extracting matches.
3. The period and exclamation mark are not letters or digits, so they separate or end tokens.
4. The underscore is also excluded. That is why the second call returns python and 3 separately.

**Practice question:** Does the underscore stay inside a token?

**Answer to explain after the pause:** No. This pattern only matches ASCII letters and digits.

**Connect to the project:** Open guide chapter 14, under **In this project**, and find the same idea in src/search.py · TOKEN_PATTERN and tokenize. Explain how the small example relates to that code.

**Transition:** Next, we will look at counting words with counter.


## Slide 15 — Counting words with Counter

**Goal:** Counter maps each item to its frequency.

**Explain:**

Counter is a word tally. One Counter tells us how often each word occurs in a chunk. A second Counter measures how many chunks contain that word. Those are different questions. The second calculation iterates over keys, so a word repeated ten times in one chunk contributes one to its document frequency.

**Show the example — Count repeated words:**

```python
from collections import Counter

counts = Counter(["python", "python", "notes"])
print(counts["python"])
print(counts["missing"])
print(sum(counts.values()))
```

**Ask before revealing:** “What do you think this will print?” Pause while the learner reads the code. Then expand **Show expected output** on the slide.

```text
2
0
3
```

**Explain the example, one step at a time:**

1. Counter receives a list containing python twice and notes once.
2. `counts["python"]` looks up python’s frequency: 2.
3. A missing Counter key returns 0.
4. `.values()` supplies the stored frequencies. `sum(...)` adds 2 and 1 to get 3.

**Practice question:** Which counts the total tokens: len(counts) or sum(counts.values())?

**Answer to explain after the pause:** sum(counts.values()) gives 3 tokens. len(counts) gives 2 distinct terms.

**Connect to the project:** Open guide chapter 15, under **In this project**, and find the same idea in src/search.py · KeywordRetriever.__init__. Explain how the small example relates to that code.

**Transition:** Next, we will look at comprehensions and generators.


## Slide 16 — Comprehensions and generators

**Goal:** [expression for item in items] builds a list.

**Explain:**

These compact expressions are loops in a smaller space. Square brackets build a list immediately. A dictionary comprehension builds key-value entries. A generator feeds one result at a time to something like sum or Counter. Read multiple for clauses from left to right: first choose a chunk’s counts, then visit each key in those counts.

**Show the example — Build and consume values:**

```python
words = ["Python", "Notes"]
lowercase = [word.lower() for word in words]
lengths = (len(word) for word in words)
print(lowercase)
print(sum(lengths))
```

**Ask before revealing:** “What do you think this will print?” Pause while the learner reads the code. Then expand **Show expected output** on the slide.

```text
['python', 'notes']
11
```

**Explain the example, one step at a time:**

1. The list contains two strings.
2. The square-bracket comprehension calls lower on each string and collects both results.
3. The parenthesized generator describes how to supply each word’s length when requested.
4. `sum(lengths)` consumes lengths 6 and 5 and returns 11. The generator is then exhausted.

**Practice question:** Which expression creates a list immediately?

**Answer to explain after the pause:** The square-bracket comprehension. The generator supplies lengths as sum consumes them.

**Connect to the project:** Open guide chapter 16, under **In this project**, and find the same idea in src/search.py · index construction and score calculation. Explain how the small example relates to that code.

**Transition:** Next, we will look at arithmetic and the search score.


## Slide 17 — Arithmetic and the search score

**Goal:** & finds shared terms.

**Explain:**

First find shared words. For each shared word, cap its count at three and multiply by its rarity weight. Add those contributions, then divide by the square root of the retained-token count. With python python notes and notes only, the first chunk scores about one point six two three for python. That is a ranking score, not a probability. Repeating python in the query does not change it because the query uses a set.

**Show the example — Calculate a score:**

```python
from src.models import DocumentChunk
from src.search import KeywordRetriever

chunks = [DocumentChunk("a", 1, "python python notes"),
          DocumentChunk("b", 1, "notes only")]
result = KeywordRetriever(chunks).search("python")[0]
print(f"{result.score:.3f}")
```

**Ask before revealing:** “What do you think this will print?” Pause while the learner reads the code. Then expand **Show expected output** on the slide.

```text
1.623
```

**Explain the example, one step at a time:**

1. Create two passages so the search can compare word frequencies across them.
2. Build a KeywordRetriever and search for python.
3. Only passage a contains python, so `[0]` selects that result.
4. The f-string displays its stored score rounded to three decimal places. The project formula is explained below.

**Practice question:** Is 1.623 a probability?

**Answer to explain after the pause:** No. It is a relative ranking score, not a confidence percentage.

**Connect to the project:** Open guide chapter 17, under **In this project**, and find the same idea in src/search.py · KeywordRetriever.search. Explain how the small example relates to that code.

**Transition:** Next, we will look at sorting, lambdas, and result limits.


## Slide 18 — Sorting, lambdas, and result limits

**Goal:** lambda defines a small unnamed function.

**Explain:**

Sorting asks each result for a comparison key. Lambda is a small function that supplies three priorities. First comes negative score, so larger real scores sort earlier. A tie falls through to filename and then chunk number. Finally, the slice keeps the requested number of results. The early guard is what gives negative limits the intended empty-result behavior.

**Show the example — Sort by a key:**

```python
scores = [("b.txt", 2.0), ("a.txt", 2.0), ("c.txt", 3.0)]
ranked = sorted(scores, key=lambda item: (-item[1], item[0]))
print(ranked[:2])
```

**Ask before revealing:** “What do you think this will print?” Pause while the learner reads the code. Then expand **Show expected output** on the slide.

```text
[('c.txt', 3.0), ('a.txt', 2.0)]
```

**Explain the example, one step at a time:**

1. Each tuple holds a filename and its score.
2. The lambda gives sorted a two-part key: negative score first, filename second.
3. A score of 3 becomes -3, which sorts before -2. Equal scores fall through to filename order.
4. `ranked[:2]` takes the first two results without changing the original scores list.

**Practice question:** Why does a.txt come before b.txt?

**Answer to explain after the pause:** Their scores tie, so the next tuple element, the filename, decides their order.

**Connect to the project:** Open guide chapter 18, under **In this project**, and find the same idea in src/search.py · end of KeywordRetriever.search. Explain how the small example relates to that code.

**Transition:** Next, we will look at command-line arguments and execution.


## Slide 19 — Command-line arguments and execution

**Goal:** argparse converts command text into values.

**Explain:**

Argparse turns the command you type into usable Python values. Type equals int passes the conversion function itself. Verbose is a switch. The search subcommand owns the query, limit, retriever choice, and semantic cache/offline options. At the bottom, the module guard runs main only when this module is the entry point. Main returns a status number, and SystemExit gives that status to the shell.

**Show the example — Parse command options:**

```python
from src.cli import build_parser

args = build_parser().parse_args(["--verbose", "search", "python", "--limit", "2"])
print(args.verbose)
print(args.query)
print(args.limit)
```

**Ask before revealing:** “What do you think this will print?” Pause while the learner reads the code. Then expand **Show expected output** on the slide.

```text
True
python
2
```

**Explain the example, one step at a time:**

1. `build_parser()` creates the parser configured by the project.
2. Passing a list to parse_args lets this example supply command-line words directly.
3. `--verbose` turns on a flag; search selects the subcommand; python is the query.
4. `--limit 2` is converted to an integer. The print calls read the resulting attributes.

**Practice question:** Where does --verbose go relative to search?

**Answer to explain after the pause:** Before search, because it belongs to the main parser.

**Connect to the project:** Open guide chapter 19, under **In this project**, and find the same idea in src/cli.py · build_parser, main, and module guard. Explain how the small example relates to that code.

**Transition:** Next, we will look at printing, formatting, and logging.


## Slide 20 — Printing, formatting, and logging

**Goal:** f-strings insert expression values inside braces.

**Explain:**

An f-string fills in values between braces. The colon dot three f says to show three decimal places. Printing a rounded score does not change the number used for sorting. Logging is for diagnostics. Info summaries remain visible in ordinary runs, while verbose enables the detailed debug messages. Logging placeholders use a different formatting style from f-strings.

**Show the example — Format a number:**

```python
score = 1.622891
print(f"Score: {score:.3f}")
print(score)
```

**Ask before revealing:** “What do you think this will print?” Pause while the learner reads the code. Then expand **Show expected output** on the slide.

```text
Score: 1.623
1.622891
```

**Explain the example, one step at a time:**

1. Assign a decimal number to score.
2. The f prefix allows the braces to contain a Python expression.
3. Inside the braces, `:.3f` requests three digits after the decimal point.
4. The final print displays the original value, showing that formatting did not change it.

**Practice question:** Did formatting change the value stored in score?

**Answer to explain after the pause:** No. It changes only the displayed text.

**Connect to the project:** Open guide chapter 20, under **In this project**, and find the same idea in src/cli.py · output; src/loader.py · LOGGER. Explain how the small example relates to that code.

**Transition:** Next, we will look at exceptions and context managers.


## Slide 21 — Exceptions and context managers

**Goal:** raise signals an exceptional condition.

**Explain:**

Raising an exception stops the normal path and reports a problem to the caller. The chunker uses ValueError when its settings do not make sense. In the test, with pytest raises sets an expectation around the call. A ValueError makes that expectation pass. No error would make the test fail. The application itself does not catch these chunk-setting errors.

**Show the example — Expect an exception:**

```python
import pytest
from src.chunker import chunk_document
from src.models import Document

with pytest.raises(ValueError):
    chunk_document(Document("note.txt", "hello"), chunk_size=3, overlap=3)
print("Expected error confirmed")
```

**Ask before revealing:** “What do you think this will print?” Pause while the learner reads the code. Then expand **Show expected output** on the slide.

```text
Expected error confirmed
```

**Explain the example, one step at a time:**

1. Import pytest and the project objects needed for the call.
2. `with pytest.raises(ValueError):` starts a block that expects a ValueError.
3. The call supplies an overlap equal to its chunk size. The chunker rejects it.
4. Pytest catches the expected exception, and execution continues to the print. If no ValueError were raised, the check would fail.

**Practice question:** Why is overlap=3 invalid when chunk_size=3?

**Answer to explain after the pause:** The step would be zero, so the windows would not advance.

**Connect to the project:** Open guide chapter 21, under **In this project**, and find the same idea in src/chunker.py · src/models.py · tests/test_chunker.py. Explain how the small example relates to that code.

**Transition:** Next, we will look at tests, fixtures, and assertions.


## Slide 22 — Tests, fixtures, and assertions

**Goal:** pytest discovers test_ functions.

**Explain:**

A test calls real code and checks what happened. Pytest supplies the temporary directory because the function requests the fixture by name. The list comprehension pulls out exactly the fields the test wants to compare. Other tests check overlap, ranking, and empty input. Tests are executable examples of expected behavior, so they are a useful place to learn the application.

**Show the example — Check an expectation:**

```python
from src.search import tokenize

assert tokenize("PYTHON!") == ["python"]
print("Check passed")
```

**Ask before revealing:** “What do you think this will print?” Pause while the learner reads the code. Then expand **Show expected output** on the slide.

```text
Check passed
```

**Explain the example, one step at a time:**

1. Call tokenize with uppercase text and punctuation.
2. `== ["python"]` compares its result with the expected list.
3. `assert` checks that the comparison is true.
4. Because it is true, execution reaches print. A false assertion would stop the normal path with AssertionError.

**Practice question:** What happens if an assertion is false?

**Answer to explain after the pause:** Python raises AssertionError, and pytest reports the test as failed.

**Connect to the project:** Open guide chapter 22, under **In this project**, and find the same idea in tests/test_loader.py · tests/test_chunker.py · tests/test_search.py. Explain how the small example relates to that code.

**Transition:** Next, we will look at running and tracing the project.


**Testing walkthrough:** Open `tests/test_hybrid.py` and read `test_worked_example_uses_order_not_scores`. Identify arranged rankings, the fusion call, and assertions. Then show `tests/test_semantic_integration.py`: it uses the real cached model. Explain that 122 default cases and five integration cases count parametrized inputs, not just functions. Run `.venv/bin/python -m pytest -v`; show how `PASSED`, `FAILED`, and `deselected` differ. For real-model checks use `.venv-semantic/bin/python -m pytest -m integration -v` with the cache prepared. Finally show `evaluations/hybrid-results.md`: passing correctness checks coexists with hybrid's 75% Hit@3 versus semantic's 85%. Ask the learner which evidence answers “does it work as specified?” and which answers “does it retrieve the right passage?”

## Slide 23 — Running and tracing the project

**Goal:** Use Python 3.10 or newer.

**Explain:**

These commands run in a terminal from the project root. The virtual environment keeps dependencies together, and the editable install makes local source changes available. Remember that pyproject is configuration, not Python. To finish, trace one search from arguments to documents to chunks to results. Predict the three practice answers before checking the guide: tokens python and three, three chunks, and a set removes repeated query terms.

**Show the example — Trace the full workflow:**

```python
from src.models import Document
from src.chunker import chunk_documents
from src.search import KeywordRetriever

notes = [Document("note.txt", "python notes are useful")]
chunks = chunk_documents(notes)
results = KeywordRetriever(chunks).search("python")
print(results[0].chunk.text)
```

**Ask before revealing:** “What do you think this will print?” Pause while the learner reads the code. Then expand **Show expected output** on the slide.

```text
python notes are useful
```

**Explain the example, one step at a time:**

1. Create a list containing one Document, representing a loaded note.
2. `chunk_documents(notes)` converts documents into a list of searchable passages.
3. `KeywordRetriever(chunks).search("python")` prepares the index and searches it.
4. Select the first result, access its chunk, and print that chunk’s text. This follows the same data flow as the CLI.

**Practice question:** Which objects connect chunk_documents to KeywordRetriever?

**Answer to explain after the pause:** DocumentChunk objects, collected in a list.

**Connect to the project:** Open guide chapter 23, under **In this project**, and find the same idea in README.md · pyproject.toml · src/cli.py. Explain how the small example relates to that code.

**Transition:** Invite the learner to open src/cli.py and trace a complete search using the guide.



## Slide 24 — Stop-word filtering with frozenset

**Goal:** Explain immutable membership checks and filtering without changing source passages.

**Explain:** A frozenset stores unique values and cannot be changed in place. The project uses one for its fixed 26-word stop-word vocabulary. The list comprehension keeps each normalized token only if it is not in that vocabulary. It preserves token order and duplicates, so counts still work.

**Show the example:** Run [chapter 24](python-for-dummies.md#chapter-24). Ask learners to predict each output. `THE theory is useful` becomes `['theory', 'useful']`; `the is how` becomes an empty list. Negation, numbers, and repeated meaningful words remain.

**Connect to the project:** Both queries and passages use this function. Retained tokens determine matching and length normalization; original text and chunk boundaries stay intact. Empty-token chunks are skipped before scoring, but remain in the IDF corpus size.

**Demonstrate:** Query the two-passage example in chapter 24. The filler passage previously ranked first at 3.442672. Now only the retrieval passage matches, at 0.702733. The assertions verify that adding stop words to a query does not change its results or scores. The stop-word milestone had nine tests; current validation is 122 deterministic tests plus 5 real-model checks.

**Ask:** Why does theory survive but THE disappear? Why retain not?

**Answer:** Matching is against complete lowercase tokens. Negation can carry meaning, but retaining it does not make keyword search understand sentence meaning. The fixed English list can remove meaningful title words and has no override.


## Slide 25 — Semantic search, vectors, and optional dependencies

**Goal:** Separate vector arithmetic, model behavior, and dependency setup.

**Explain:** A model represents text as numbers. Normalize a vector by dividing by its length, then compare unit vectors with a dot product. Similarity is not a probability. We are still returning passages with sources, not generating answers.

**Show the example:**

```python
import math

# Length 5 turns [3, 4] into a unit vector; magnitude no longer affects similarity.
passage = [3.0, 4.0]
length = math.sqrt(sum(value * value for value in passage))
unit = [value / length for value in passage]
query = [1.0, 0.0]  # Already length one.
print(unit)
print(sum(a * b for a, b in zip(unit, query)))
```

**Expected output:**

```text
[0.6, 0.8]
0.6
```

**Explain step by step:** 3 squared plus 4 squared gives 25. Its square root is 5. Dividing gives 0.6 and 0.8. Pair those with 1 and 0 and sum the products to get 0.6.

**Connect to the project:** Run the second [chapter 25 example](python-for-dummies.md#chapter-25). Its fake encoder satisfies the Protocol through an encode method. Dependency injection keeps the example free of model downloads. The retriever validates vectors, snapshots chunks, encodes passages once, and preserves original text.

**Live model setup:** Install the semantic extra, run an online search to populate the pinned cache, then repeat with `--offline`. Explain lazy imports: blank requests do not load the model. Model files persist; passage vectors do not. The workspace's optional dependencies are in `.venv-semantic`.

**Evidence:** 122 deterministic tests and five real-model checks pass. Both predefined paraphrases recovered their expected passage first. Unrelated questions also returned passages, so nearest does not establish relevance. The model keeps stop words and warns when its own token limit truncates input.

**Ask:** Can the fake prove actual paraphrase retrieval? Is 0.6 confidence?

**Answer:** No. The fake tests arithmetic and data flow; real-model checks test the fixed labeled cases. Cosine is similarity, not calibrated confidence.


**Follow the real path:** Run the keyword-only environment with `.venv/bin/python -m src.cli search "finding information" --retriever keyword`, then the prepared semantic environment with `.venv-semantic/bin/python -m src.cli search "finding information" --retriever semantic --offline`. On a fresh checkout, install the extra and populate the cache online first. Trace chunks → adapter → passage vectors → query vector → cosine → shared result objects. A new process reuses model files but rebuilds passage vectors.

**Clarify test layers:** Default tests use deterministic fakes. `python -m pytest -m integration -s -q` explicitly uses the actual cached model with network calls blocked. A fake cannot validate model quality, and six labeled queries cannot establish general accuracy.


## Slide 26 — Hybrid search with reciprocal ranks

**Goal:** Combine ranked evidence without adding incompatible score scales.

**Show:** Run both [chapter 26 examples](python-for-dummies.md#chapter-26). The first prints A 0.032522, C 0.016393, B 0.016129. The second shows semantic selecting answer.md and hybrid incorrectly promoting noise.md. Neither example needs model dependencies.

**Explain:** enumerate starts at one to represent rank. Each branch has its own seen set, and a tuple of filename and chunk number identifies a passage. setdefault preserves the first original chunk. Repeated identities vote once per branch; conflicting text is an error. fsum adds contributions, then a sort and slice select the final output.

**Connect to the project:** HybridRetriever composes two existing retrievers. It snapshots the inputs, reuses both indexes, and requests all N candidates before limiting fused output. The output limit never changes the branch candidate depth. The shared SearchResult still contains original source text, but its score now means reciprocal-rank agreement.

**Evidence:** The fixed 23-question comparison shows hybrid at 75% Hit@3 and semantic at 85%. Hybrid recovers one semantic miss and loses three semantic hits. The feature remains opt-in; ranking agreement is not proof of relevance.

**Run:** `.venv-semantic/bin/python -m src.cli search "finding information" --retriever hybrid --offline`. Use the existing pinned model cache. Model failure ends the operation without partial keyword results. Blank requests invoke neither branch.

**Ask:** Would rescaling keyword scores change the fused order? No, unless the branch order changes. Why not request only the desired top one from each branch? A lower-ranked agreement may win after fusion, and changing display limits should not change ranking.


## Slide 27 — Local answers, JSON, and generator protocols

**Goal:** Follow retrieval into one generated, validated answer with source citations.

**Show:** Run both chapter 27 examples. The fake generator prints “Backups run Friday. [S1]” and the original source. The second rejects S99. Neither example needs a running model.

**Explain:** The Protocol is a method contract, not a model. JSON is data serialization, not Python execution. A frozen Context retains exact evidence; Claim and Answer hold validated output. The runtime adapter closes sockets with finally, uses monotonic deadlines, and never follows redirects or proxies. The client and server are separate processes, so offline validation must cover both.

**Runtime walkthrough:** MiniLM embeds notes for semantic retrieval; Qwen generates text through Ollama. Use the README setup with cloud disabled and installed assets. Ask defaults to semantic; search still defaults to keyword. Keep download/setup separate from normal inference. No hosted API fee is involved, but local RAM, disk, and time are used.

**Practice:** Can a known S1 citation still be misleading? Yes: it could ignore a conflicting S2. The small model also over-abstains in an injection-adjacent case, and that quality test remains failed. Show the manual evaluation, not just a passing JSON validator.

**Connect:** Trace `answer_question`, `LocalGenerator.generate`, `validate_answer`, and `render_answer`. Explain that an unavailable server is an error; insufficient evidence is a distinct successful outcome. There is no automatic fallback or retry.
