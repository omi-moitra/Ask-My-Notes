# Python for Dummies: Ask My Notes

Learn Python one example at a time, using the code in Ask My Notes.

**Companions:** [Presenter script](python-for-dummies-script.md) · [HTML slideshow](python-for-dummies-slideshow.html)

Read the chapters in order for a first lesson, or use the coverage index at the end while reading source code. Every chapter has the same number as its slide and narration segment. Chapters 1–23 introduce the base Python and keyword workflow; chapters 24–26 explain filtering, semantic retrieval, and hybrid fusion. Code with comments describing output is illustrative; shortened excerpts are identified. The pipeline arrows and terminal commands are not Python source.

## How to use this tutorial

Start with the short explanation. Run the small example, compare your output, then try the exercise. Read **In this project** to connect the idea to the real application.

**Before you start:** use Python 3.10 or newer. From the project root, activate the existing environment with `source .venv/bin/activate`. If it is not configured yet, follow [the setup instructions](README.md#install). Copy each complete **Try it locally** example into a temporary `.py` file in the project root and run it with `python filename.py`. Each example includes its own imports. Chapter 21 also needs the project's `pytest` development dependency. The HTML deck shows expected output; it does not execute Python in the browser.

**Learning path:** basics (1–6) → collections and control flow (7–10) → objects and files (11–13) → search logic (14–18) → CLI and tests (19–23) → stop-word filtering (24) → semantic retrieval (25) → hybrid fusion (26) → local grounded answers (27).

## Lessons

1. [The program you are learning](#chapter-1)
2. [Files, modules, and imports](#chapter-2)
3. [Indentation, comments, and docstrings](#chapter-3)
4. [Names, values, and basic types](#chapter-4)
5. [Functions, arguments, and return values](#chapter-5)
6. [Type hints describe expected values](#chapter-6)
7. [Lists, tuples, sets, and dictionaries](#chapter-7)
8. [Conditions and truthiness](#chapter-8)
9. [Loops, ranges, and unpacking](#chapter-9)
10. [Strings, indexes, and slices](#chapter-10)
11. [Classes, instances, and dataclasses](#chapter-11)
12. [Methods, self, and inheritance](#chapter-12)
13. [Paths and reading files](#chapter-13)
14. [Regular expressions and tokens](#chapter-14)
15. [Counting words with Counter](#chapter-15)
16. [Comprehensions and generators](#chapter-16)
17. [Arithmetic and the search score](#chapter-17)
18. [Sorting, lambdas, and result limits](#chapter-18)
19. [Command-line arguments and execution](#chapter-19)
20. [Printing, formatting, and logging](#chapter-20)
21. [Exceptions and context managers](#chapter-21)
22. [Tests, fixtures, and assertions](#chapter-22)
23. [Running and tracing the project](#chapter-23)
24. [Stop-word filtering with frozenset](#chapter-24)
25. [Semantic search, vectors, and optional dependencies](#chapter-25)
26. [Hybrid search with reciprocal ranks](#chapter-26)
27. [Local answers, JSON, and generator protocols](#chapter-27)

Testing reference: [Test files](#where-the-tests-live) · [Commands and results](#running-and-reading-test-results)

Reference: [Source coverage](#source-coverage-index) · [Quick syntax](#quick-syntax-reference) · [What you do not need yet](#what-you-do-not-need-yet)

<a id="chapter-1"></a>

## 1. The program you are learning

Read local notes.

### Try it locally: Search a tiny note

```python
from src.models import DocumentChunk
from src.search import KeywordRetriever

chunk = DocumentChunk("note.txt", 1, "Python makes notes searchable")
results = KeywordRetriever([chunk]).search("python")
print(results[0].chunk.source)
```

**Output**

```text
note.txt
```

### Example explained

1. `DocumentChunk(...)` creates one searchable passage. Its three arguments are the filename, chunk number, and text.
2. `[chunk]` puts that passage in a list. `KeywordRetriever([chunk])` prepares the list for searching.
3. `.search("python")` returns matching results. `[0]` selects the first result.
4. `result.chunk.source` follows the result to its passage and then its filename. `print(...)` displays it.

### In this project

**Source:** src/cli.py · main

The following is a project excerpt or teaching diagram. Read it alongside the explanation; it may depend on surrounding code.

```text
documents → load_documents → chunk_documents
          → selected retriever → search → print
             keyword (default), semantic, or hybrid (optional model)
```

Ask My Notes searches local `.md` and `.txt` files. It returns passages and their filenames. Keyword mode uses ordinary Python token matching; optional semantic mode runs a local embedding model. Hybrid combines the two rankings. These three retrievers return passages; the separate `ask` command uses them to generate a local answer with citations (chapter 27). The arrows above describe the program, not executable Python.

### Reading the project code

A **program** is a set of instructions. A **value** is a piece of data, such as text or a number. A **variable** is a name that refers to a value. A **function** groups instructions you can reuse. An **object** bundles data and behavior. You will meet each idea in the order the application needs it.

Keyword search and the local HTTP adapter use Python's standard library. Semantic retrieval needs the optional embedding stack, and real answer generation needs a separate Ollama process and installed model. Tests additionally use `pytest`. This guide covers all language constructs in the project's own Python files, including the tests; it does not attempt to teach the internals of Python or installed dependencies.

> **Remember:** Read local notes.

### Exercise

What does the search return: a passage or a generated answer?

<details>
<summary>Show answer</summary>

A matching passage with its source and score.

</details>

 [All lessons](#lessons) · [Next →](#chapter-2)

---

<a id="chapter-2"></a>

## 2. Files, modules, and imports

A .py file is a module.

### Try it locally: Import a function

```python
from src.search import tokenize

print(tokenize("Hello Python!"))
```

**Output**

```text
['hello', 'python']
```

### Example explained

1. `from src.search import tokenize` makes the project’s tokenize function available by name.
2. `tokenize("Hello Python!")` passes text to that function.
3. The function returns a list of lowercase words. `print(...)` displays that returned list.

### In this project

**Source:** src/__init__.py · imports across src/ and tests/

The following is a project excerpt or teaching diagram. Read it alongside the explanation; it may depend on surrounding code.

```python
import math
from pathlib import Path
from .models import Document
from src.chunker import chunk_document
```

`import math` makes the module available as `math`, so the code calls `math.log(...)`. `from pathlib import Path` brings in the particular name `Path` directly. Python's standard library supplies `argparse`, `logging`, `pathlib`, `dataclasses`, `math`, `re`, and `collections` here.

### Reading the project code

`src/__init__.py` marks `src` as a regular package and currently contains only a module docstring. `from .models import Document` is a relative import: find `models` in this package. Tests use absolute imports such as `from src.models import Document`.

Run the application from the project root with `python -m src.cli ...`. The `-m` option runs a module with its package context, allowing relative imports to work. Running `python src/cli.py` directly is not equivalent.

> **Remember:** A .py file is a module.

### Exercise

What does the dot in from .models import Document mean?

<details>
<summary>Show answer</summary>

Look for models inside the current package.

</details>

 [← Previous](#chapter-1) · [All lessons](#lessons) · [Next →](#chapter-3)

---

<a id="chapter-3"></a>

## 3. Indentation, comments, and docstrings

A colon starts a block.

### Try it locally: Read an indented block

```python
size = 4
# Only print when the size is positive.
if size > 0:
    print("Ready")
```

**Output**

```text
Ready
```

### Example explained

1. `size = 4` stores the number 4 under the name size.
2. `#` introduces a comment. Python does not execute the comment.
3. `if size > 0:` asks whether size is greater than zero. The colon begins its block.
4. The indented `print` runs because the condition is true. Remove the indentation and it no longer belongs to the condition.

### In this project

**Source:** src/chunker.py · chunk_document

The following is a project excerpt or teaching diagram. Read it alongside the explanation; it may depend on surrounding code.

```python
def chunk_document(document: Document,
                   chunk_size: int = 120,
                   overlap: int = 20) -> list[DocumentChunk]:
    """Create overlapping word chunks."""
    # Validate before doing any work.
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")
```

This abbreviated excerpt preserves the function signature and validation behavior. Python uses indentation to group code instead of braces. Project blocks use four spaces per level. The `raise` statement belongs to the `if`, which belongs to the function.

### Reading the project code

A `#` starts a comment through the end of that line. A triple-quoted string in the first statement of a module, class, or function is its **docstring**, available to tools such as `help()`. Triple quotes can hold several lines; they do not automatically make any string a comment.

Parentheses, square brackets, and braces allow an expression to continue across lines. A trailing comma, as in a multiline function call or tuple, is allowed. Blank lines separate ideas for readers; they do not end an indented block by themselves.

> **Remember:** A colon starts a block.

### Exercise

What happens if size becomes 0?

<details>
<summary>Show answer</summary>

The condition is false, so the indented print statement does not run.

</details>

 [← Previous](#chapter-2) · [All lessons](#lessons) · [Next →](#chapter-4)

---

<a id="chapter-4"></a>

## 4. Names, values, and basic types

= assigns; == compares.

### Try it locally: Assign a value

```python
chunk_size = 120
overlap = 20
step = chunk_size - overlap
print(step)
print(step == 100)
```

**Output**

```text
100
True
```

### Example explained

1. The first two assignments name the window size and overlap.
2. `chunk_size - overlap` subtracts 20 from 120. The result is assigned to step.
3. `print(step)` displays 100.
4. `step == 100` compares two values. Its result is the Boolean value True.

### In this project

**Source:** src/chunker.py · src/models.py · src/cli.py

The following is a project excerpt or teaching diagram. Read it alongside the explanation; it may depend on surrounding code.

```python
step = chunk_size - overlap
chunks: list[DocumentChunk] = []
# Examples of values used by this project:
120       # int
1.0       # float
"notes"   # str
True      # bool
None      # no value
```

`step = chunk_size - overlap` calculates a number and binds the name `step` to it. With defaults, the result is `100`. `int` means whole number; `float` means a floating-point number; `str` means text; `bool` is `True` or `False`. `None` represents no value and appears in the constructor's return annotation.

### Reading the project code

Single and double quotes both delimit strings. `""` is an empty string; `[]` is an empty list. A dot accesses an object's attribute or method: `document.text` retrieves data, while `document.text.split()` calls behavior. Parentheses perform a call; arguments go inside them.

Names such as `SUPPORTED_SUFFIXES`, `LOGGER`, and `TOKEN_PATTERN` are uppercase by convention to signal constants or module-level shared settings. Python does not make an uppercase name immutable. `self.chunks = chunks` stores a reference to the same list; assignment does not automatically copy objects.

> **Remember:** = assigns; == compares.

### Exercise

Which symbol assigns a value: = or ==?

<details>
<summary>Show answer</summary>

= assigns. == compares values.

</details>

 [← Previous](#chapter-3) · [All lessons](#lessons) · [Next →](#chapter-5)

---

<a id="chapter-5"></a>

## 5. Functions, arguments, and return values

def defines reusable work.

### Try it locally: Call a function

```python
def advance(size, overlap=1):
    return size - overlap

print(advance(4))
print(advance(4, overlap=2))
```

**Output**

```text
3
2
```

### Example explained

1. `def advance(size, overlap=1):` defines a function with two parameters. The second has a default.
2. `return size - overlap` calculates a value and sends it back to the caller.
3. `advance(4)` uses the default overlap of 1, so it returns 3.
4. `advance(4, overlap=2)` replaces the default, so it returns 2. This small teaching function illustrates the subtraction used by the chunker.

### In this project

**Source:** src/chunker.py · chunk_document and chunk_documents

The following is a project excerpt or teaching diagram. Read it alongside the explanation; it may depend on surrounding code.

```python
def chunk_document(document: Document,
                   chunk_size: int = 120,
                   overlap: int = 20) -> list[DocumentChunk]:
    ...

chunks = chunk_document(document, chunk_size=4, overlap=1)
```

The `...` above is an omission marker for this teaching excerpt; the real function has a body. A **parameter** is a name in a function definition. An **argument** is a value supplied by a caller. `document` is required; `chunk_size` and `overlap` default to `120` and `20`.

### Reading the project code

The call supplies `document` by position and the other values by keyword. The project also uses `chunk_document(document, chunk_size, overlap)`, where all three arguments are positional and their order matters. `return chunks` immediately ends the call and gives the list back. Early returns such as `return []` avoid unnecessary work.

Names assigned inside a function are local to that invocation unless explicitly handled otherwise. Defining a function does not run its body. Calling it does. A function that reaches the end without returning a value returns `None` implicitly.

> **Remember:** def defines reusable work.

### Exercise

Which overlap value is used by advance(4)?

<details>
<summary>Show answer</summary>

The default value, 1.

</details>

 [← Previous](#chapter-4) · [All lessons](#lessons) · [Next →](#chapter-6)

---

<a id="chapter-6"></a>

## 6. Type hints describe expected values

name: Type describes a value.

### Try it locally: Read a type hint

```python
def label(text: str) -> str:
    return text

print(label("notes"))
print(label(42))
```

**Output**

```text
notes
42
```

### Example explained

1. `text: str` describes the expected input type. `-> str` describes the expected return type.
2. `return text` gives back exactly what was passed in.
3. The first call passes a string. The second deliberately passes an integer.
4. Both run because annotations do not insert runtime checks. The second call violates the hint, which a type checker can flag.

### In this project

**Source:** src/models.py · src/chunker.py · src/search.py

The following is a project excerpt or teaching diagram. Read it alongside the explanation; it may depend on surrounding code.

```python
source: str
score: float
chunks: list[DocumentChunk] = []

def tokenize(text: str) -> list[str]:
    return [term for term in TOKEN_PATTERN.findall(text.lower()) if term not in STOP_WORDS]
```

`text: str` says the parameter is expected to be a string. `-> list[str]` says the function is expected to return a list of strings. `list[DocumentChunk]` describes the expected element type; it is not a request to create chunks. In `chunks: list[DocumentChunk] = []`, the annotation describes the variable and `[]` creates the actual list.

### Reading the project code

`-> None` on `__init__` says the initializer returns no useful value. `-> int` on `main` describes the exit-code value it returns. `-> argparse.ArgumentParser` uses a class inside an imported module as the type.

These are ordinary annotations, not automatic runtime checks. Explicit conditions and `raise ValueError` perform validation here. The project declares Python 3.10 or newer in `pyproject.toml`.

> **Remember:** name: Type describes a value.

### Exercise

Why does label(42) still run?

<details>
<summary>Show answer</summary>

Type hints describe expected types. This function has no runtime type check.

</details>

 [← Previous](#chapter-5) · [All lessons](#lessons) · [Next →](#chapter-7)

---

<a id="chapter-7"></a>

## 7. Lists, tuples, sets, and dictionaries

Lists preserve order and allow repeats.

### Try it locally: Choose a collection

```python
words = ["python", "python", "notes"]
unique_words = set(words)
weights = {"python": 2.0}
print(len(words))
print(len(unique_words))
print(weights["python"])
```

**Output**

```text
3
2
2.0
```

### Example explained

1. The list words contains three entries, including a repeated word.
2. `set(words)` produces unique entries: python and notes.
3. `{"python": 2.0}` creates a dictionary linking the key python to a number.
4. `len(...)` counts entries. `weights["python"]` retrieves the value stored under that key.

### In this project

**Source:** src/loader.py · src/search.py · tests/test_loader.py

The following is a project excerpt or teaching diagram. Read it alongside the explanation; it may depend on surrounding code.

```python
chunks = []                         # list
SUPPORTED_SUFFIXES = {".md", ".txt"}  # set
query_terms = set(tokenize(query))   # set
# Dictionary entry shape used in search.py:
# term: weight
# Tuple shape used for sorting:
# (-result.score, source, chunk_number)
```

A **list** is an ordered, mutable collection. `append(item)` adds one item. `extend(items)` adds each item from another iterable. Appending a list would nest it; extending combines its elements into the outer list. `len(chunks)` counts items.

### Reading the project code

A **tuple** groups values in a fixed order, such as `(document.source, document.text)` in a test. Commas create tuples; parentheses usually make them easier to read. Tuples do not support replacing their elements.

A **set** keeps unique values. `set(tokenize(query))` ensures repeating a query word does not increase its contribution. The suffix set supports quick membership checks. Do not rely on set iteration order. `{}` alone creates an empty dictionary, so an empty set is written `set()`.

### A closer look

A **dictionary** maps keys to values. The inverse-frequency dictionary maps a term string to its weight. `.keys()` exposes keys, `.values()` exposes values, and `.items()` exposes `(key, value)` pairs. `mapping[key]` retrieves an entry; `.get(key, 1.0)` supplies a default when absent. `Counter`, used later, is a specialized dictionary.

> **Remember:** Lists preserve order and allow repeats.

### Exercise

Why does unique_words contain only two items?

<details>
<summary>Show answer</summary>

A set stores each distinct value once.

</details>

 [← Previous](#chapter-6) · [All lessons](#lessons) · [Next →](#chapter-8)

---

<a id="chapter-8"></a>

## 8. Conditions and truthiness

if runs a block only when its condition is true.

### Try it locally: Check for empty text

```python
text = "   "
print(bool(text))
print(bool(text.strip()))
```

**Output**

```text
True
False
```

### Example explained

1. `text` contains three spaces, so it is a nonempty string.
2. `bool(text)` asks for its truth value and returns True.
3. `text.strip()` returns a new string with surrounding whitespace removed.
4. That new string is empty, so converting it to bool returns False. The original text is unchanged.

### In this project

**Source:** src/loader.py · src/chunker.py · src/cli.py

The following is a project excerpt or teaching diagram. Read it alongside the explanation; it may depend on surrounding code.

```python
if not path.is_file() or path.suffix.lower() not in SUPPORTED_SUFFIXES:
    continue

if overlap < 0 or overlap >= chunk_size:
    raise ValueError("overlap must be between zero and chunk_size - 1")

if not results:
    return 0
```

Comparisons in the project include `==`, `<`, `<=`, `>`, and `>=`. `=` is assignment, not comparison. `in` checks membership; `not in` checks absence. `not` reverses a truth value.

### Reading the project code

`or` evaluates its right side only if its left side is false. In the loader, a directory fails `is_file()`, so the suffix test is unnecessary. This is **short-circuit evaluation**.

Empty lists, sets, strings, and dictionaries, numeric zero, and `None` are false in conditions. Nonempty strings are true even if they contain only spaces. That is why `if text.strip():` first removes whitespace for the test. It does not change the original `text` stored in the document.

### A closer look

The CLI also uses a conditional expression: `logging.DEBUG if args.verbose else logging.INFO`. Unlike a multiline `if` statement, this expression chooses and produces one value.

> **Remember:** if runs a block only when its condition is true.

### Exercise

Is a string containing three spaces empty?

<details>
<summary>Show answer</summary>

No. It is nonempty until strip removes the spaces.

</details>

 [← Previous](#chapter-7) · [All lessons](#lessons) · [Next →](#chapter-9)

---

<a id="chapter-9"></a>

## 9. Loops, ranges, and unpacking

for visits items from an iterable.

### Try it locally: Number a loop

```python
for number, start in enumerate(range(0, 7, 3), start=1):
    print(number, start)
```

**Output**

```text
1 0
2 3
3 6
```

### Example explained

1. `range(0, 7, 3)` supplies the positions 0, 3, and 6.
2. `enumerate(..., start=1)` pairs those positions with the numbers 1, 2, and 3.
3. `number, start` unpacks each pair into two names.
4. The indented print runs once per pair and displays both values separated by a space.

### In this project

**Source:** src/chunker.py · src/search.py · src/cli.py

The following is a project excerpt or teaching diagram. Read it alongside the explanation; it may depend on surrounding code.

```python
for chunk_number, start in enumerate(range(0, len(words), step), start=1):
    chunk_words = words[start : start + chunk_size]

for chunk, counts in zip(self.chunks, self.term_counts):
    matched_terms = query_terms & counts.keys()
```

An **iterable** can supply items one at a time. `for document in documents:` assigns each item to `document` and runs the body for it.

### Reading the project code

`range(0, len(words), step)` produces starting positions from zero up to, but excluding, the word count. `enumerate(..., start=1)` pairs each position with a one-based number. The loop unpacks those pairs into `chunk_number` and `start`. Here `start=1` controls the counter, not the word positions.

`zip(self.chunks, self.term_counts)` pairs each chunk with its precomputed counts. Normally it stops at the shorter iterable; these two lists are built to have equal length. `continue` skips to the next iteration. `break` exits the current loop altogether. `return` exits the entire function, which is a different scope.

> **Remember:** for visits items from an iterable.

### Exercise

Why is there no start position 7?

<details>
<summary>Show answer</summary>

range excludes its stop value. With a step of 3, the positions here are 0, 3, and 6.

</details>

 [← Previous](#chapter-8) · [All lessons](#lessons) · [Next →](#chapter-10)

---

<a id="chapter-10"></a>

## 10. Strings, indexes, and slices

Indexes start at zero.

### Try it locally: Slice a list

```python
words = "one two three four five six seven".split()
for start in range(0, len(words), 3):
    print(" ".join(words[start:start + 4]))
```

**Output**

```text
one two three four
four five six seven
seven
```

### Example explained

1. `.split()` changes a sentence into a list of seven words.
2. The range supplies starting positions 0, 3, and 6.
3. `words[start:start + 4]` selects up to four words. Its stop position is excluded.
4. `" ".join(...)` combines the selected words with spaces. At start 6, only the word seven remains.

### In this project

**Source:** src/chunker.py · tests/test_chunker.py

The following is a project excerpt or teaching diagram. Read it alongside the explanation; it may depend on surrounding code.

```python
words = document.text.split()
# ["one", "two", "three", "four", "five", "six", "seven"]
chunk_words = words[start : start + chunk_size]
text = " ".join(chunk_words)

# chunk_size=4, overlap=1 → step=3
# words[0:4] → one two three four
# words[3:7] → four five six seven
# words[6:10] → seven
```

`split()` without an argument splits on whitespace and discards empty pieces. `" ".join(chunk_words)` combines strings with a single space between them, so chunk text does not preserve original spacing.

### Reading the project code

`items[0]` gets the first item, as in `results[0]`. A slice `items[start:stop]` gets a new list with positions from `start` through `stop - 1`. A stop beyond the list's end is safely clipped. `[:limit]` omits the start and therefore begins at zero. A single out-of-range index raises `IndexError`, unlike an oversized slice stop.

With seven words, size four, and overlap one, `step` is three and the starts are `0, 3, 6`. The actual project produces **three** chunks, including the final one-word chunk. This is explicitly tested. `lower()` returns lowercase text; `strip()` removes leading and trailing whitespace. Strings are immutable, so these methods return new strings.

> **Remember:** Indexes start at zero.

### Exercise

How many chunks does this example produce?

<details>
<summary>Show answer</summary>

Three, including the final one-word chunk.

</details>

 [← Previous](#chapter-9) · [All lessons](#lessons) · [Next →](#chapter-11)

---

<a id="chapter-11"></a>

## 11. Classes, instances, and dataclasses

A class defines a kind of object.

### Try it locally: Create a document

```python
from src.models import Document

note = Document(source="note.txt", text="Hello")
print(note.source)
print(note.text)
```

**Output**

```text
note.txt
Hello
```

### Example explained

1. The import brings in the project’s Document class.
2. `Document(...)` creates one instance, with source and text supplied by name.
3. `note.source` reads the instance’s source field.
4. `note.text` reads its text field. The two print calls show these values on separate lines.

### In this project

**Source:** src/models.py · Document, DocumentChunk, SearchResult

The following is a project excerpt or teaching diagram. Read it alongside the explanation; it may depend on surrounding code.

```python
@dataclass(frozen=True)
class Document:
    source: str
    text: str

document = Document("note.txt", "Python is readable.")
# document.source → "note.txt"
```

`class Document:` defines a new type. `Document(...)` constructs an instance of it. The `@dataclass(frozen=True)` line is a **decorator**: it processes the class definition and adds behavior. It generates an initializer from the fields, a useful representation, and equality comparison based on fields.

### Reading the project code

`Document` holds `source` and `text`. `DocumentChunk` adds `chunk_number`. `SearchResult` holds a chunk object and its floating-point score. `result.chunk.source` follows those nested attributes.

`frozen=True` prevents normal reassignment of fields after construction. It is not a guarantee that every object nested inside a field is deeply immutable. In this project the document fields themselves are strings and integers. Constructors can use positional arguments, as tests do, or keywords such as `Document(source="note.txt", text="hello")`.

> **Remember:** A class defines a kind of object.

### Exercise

What is note: a class or an instance?

<details>
<summary>Show answer</summary>

An instance of the Document class.

</details>

 [← Previous](#chapter-10) · [All lessons](#lessons) · [Next →](#chapter-12)

---

<a id="chapter-12"></a>

## 12. Methods, self, and inheritance

A method is a function attached to a class.

### Try it locally: Use an instance method

```python
from src.models import DocumentChunk
from src.search import KeywordRetriever

retriever = KeywordRetriever([DocumentChunk("a.txt", 1, "python")])
print(len(retriever.chunks))
print(len(retriever.search("python")))
```

**Output**

```text
1
1
```

### Example explained

1. `DocumentChunk(...)` creates a passage and square brackets put it in a list.
2. `KeywordRetriever(...)` initializes an instance with that list.
3. `retriever.chunks` accesses the list stored on the instance; its length is 1.
4. `retriever.search("python")` calls a method on that same instance. Python supplies self, and the search returns one match.

### In this project

**Source:** src/models.py · Retriever; src/search.py · KeywordRetriever

The following is a project excerpt or teaching diagram. Read it alongside the explanation; it may depend on surrounding code.

```python
class KeywordRetriever(Retriever):
    def __init__(self, chunks: list[DocumentChunk]) -> None:
        self.chunks = chunks
        # More index-building code follows.

# Construct an instance, then call its method:
results = KeywordRetriever(chunks).search(query, limit=3)
```

`KeywordRetriever(Retriever)` declares inheritance: `KeywordRetriever` is a subclass of `Retriever`. The base class supplies a `search` method that raises `NotImplementedError`. This is a convention for a required implementation; it is not an enforced abstract class using `abc`. Instantiating `Retriever()` is allowed, but calling its unimplemented search fails.

### Reading the project code

`__init__` initializes an instance when it is constructed. Double underscores are part of this special method's name. `self` is the conventional first parameter of an instance method. Python provides it automatically when you call `retriever.search(query)`; you do not pass it yourself.

`self.chunks`, `self.term_counts`, and `self.inverse_document_frequency` persist on that instance for later searches. Local variables such as `query_terms` belong to an individual call. The subclass overrides `search` with the real ranking algorithm. No call to `super()` appears in this project.

> **Remember:** A method is a function attached to a class.

### Exercise

Do you pass self when calling retriever.search("python")?

<details>
<summary>Show answer</summary>

No. Python supplies the instance automatically.

</details>

 [← Previous](#chapter-11) · [All lessons](#lessons) · [Next →](#chapter-13)

---

<a id="chapter-13"></a>

## 13. Paths and reading files

Path represents a filesystem path.

### Try it locally: Work with a path

```python
from pathlib import Path

path = Path("documents") / "note.md"
print(path.suffix)
print(path.relative_to("documents").as_posix())
```

**Output**

```text
.md
note.md
```

### Example explained

1. `Path("documents")` represents a directory path.
2. For Path objects, `/ "note.md"` joins a filename to that path.
3. `.suffix` reads the extension, including the leading dot.
4. `.relative_to("documents")` removes the directory prefix; `.as_posix()` turns the remaining path into text with forward slashes.

### In this project

**Source:** src/loader.py · load_documents

The following is a project excerpt or teaching diagram. Read it alongside the explanation; it may depend on surrounding code.

```python
for path in sorted(directory.rglob("*")):
    if not path.is_file() or path.suffix.lower() not in SUPPORTED_SUFFIXES:
        continue
    text = path.read_text(encoding="utf-8")
    if text.strip():
        documents.append(Document(
            source=path.relative_to(directory).as_posix(), text=text))
```

`Path("documents")` represents a relative path resolved from the working directory. `directory.rglob("*")` recursively yields matching paths. The star is a glob wildcard, not Python multiplication in this context. `sorted(...)` puts the paths in a predictable order.

### Reading the project code

`is_file()` checks whether an entry is a file. `suffix` is its extension, such as `.md`. Calling `.lower()` lets `.MD` pass the same filter. `read_text(encoding="utf-8")` opens, reads, decodes, and closes the file. Read and decoding errors are not caught by this loader and can propagate to the caller.

`relative_to(directory)` removes the collection-root prefix from the recorded path. `as_posix()` formats it using forward slashes. In tests, `tmp_path / "nested" / "note.md"` joins paths because `Path` defines what `/` means for path objects. `mkdir()` creates a directory; `write_text(...)` writes a string to a file.

> **Remember:** Path represents a filesystem path.

### Exercise

Does constructing this Path create the file?

<details>
<summary>Show answer</summary>

No. A Path represents a location. Creating or writing a file is a separate operation.

</details>

 [← Previous](#chapter-12) · [All lessons](#lessons) · [Next →](#chapter-14)

---

<a id="chapter-14"></a>

## 14. Regular expressions and tokens

re.compile prepares a pattern.

### Try it locally: Split text into tokens

```python
from src.search import tokenize

print(tokenize("Python 3.10!"))
print(tokenize("Python_3!"))
```

**Output**

```text
['python', '3', '10']
['python', '3']
```

### Example explained

1. Import the project’s tokenize function so you can try its actual behavior.
2. The function lowercases Python before extracting matches.
3. The period and exclamation mark are not letters or digits, so they separate or end tokens.
4. The underscore is also excluded. That is why the second call returns python and 3 separately.

### In this project

**Source:** src/search.py · TOKEN_PATTERN and tokenize

The following is a project excerpt or teaching diagram. Read it alongside the explanation; it may depend on surrounding code.

```python
TOKEN_PATTERN = re.compile(r"[a-z0-9]+")

def tokenize(text: str) -> list[str]:
    return [term for term in TOKEN_PATTERN.findall(text.lower()) if term not in STOP_WORDS]

# tokenize("Python 3.10!")
# → ["python", "3", "10"]
```

A **regular expression** is a small pattern language for matching text. `[a-z0-9]` means one lowercase ASCII letter or digit; `+` means one or more consecutive matches. `r"..."` is a raw string literal, which preserves backslashes for patterns that use them; this particular pattern has no backslashes.

### Reading the project code

The tokenizer lowercases first, finds matches, then excludes the fixed stop-word vocabulary. Punctuation and spaces separate terms. An underscore is not included. Non-ASCII letters are not included by this pattern either. `"don't"` becomes `['don', 't']`. `retrieval` and `retrieving` remain different words: there is no stemming or synonym handling.

Chunking uses whitespace words; keyword scoring uses these filtered regex tokens. Semantic mode instead uses the embedding model’s tokenizer. Those are different boundaries. In keyword mode, a chunk containing only punctuation or stop words has no retained tokens and cannot match. Semantic mode still encodes nonblank text.

> **Remember:** re.compile prepares a pattern.

### Exercise

Does the underscore stay inside a token?

<details>
<summary>Show answer</summary>

No. This pattern only matches ASCII letters and digits.

</details>

 [← Previous](#chapter-13) · [All lessons](#lessons) · [Next →](#chapter-15)

---

<a id="chapter-15"></a>

## 15. Counting words with Counter

Counter maps each item to its frequency.

### Try it locally: Count repeated words

```python
from collections import Counter

counts = Counter(["python", "python", "notes"])
print(counts["python"])
print(counts["missing"])
print(sum(counts.values()))
```

**Output**

```text
2
0
3
```

### Example explained

1. Counter receives a list containing python twice and notes once.
2. `counts["python"]` looks up python’s frequency: 2.
3. A missing Counter key returns 0.
4. `.values()` supplies the stored frequencies. `sum(...)` adds 2 and 1 to get 3.

### In this project

**Source:** src/search.py · KeywordRetriever.__init__

The following is a project excerpt or teaching diagram. Read it alongside the explanation; it may depend on surrounding code.

```python
# tokenize removes stop words before Counter measures occurrences.
self.term_counts = [Counter(tokenize(chunk.text)) for chunk in chunks]

document_frequency = Counter(
    term for counts in self.term_counts for term in counts.keys()
)
```

`Counter(["python", "python", "notes"])` records `python: 2` and `notes: 1`. `counts[term]` reads a count; for a missing key, a Counter returns zero. `.keys()` visits each distinct term once. `.values()` supplies the frequencies, so `sum(counts.values())` is the number of regex tokens in that chunk.

### Reading the project code

The first line builds one Counter per chunk. The second passes an iterable of terms to another Counter. For each chunk's Counter, it visits the keys, not all repeated occurrences. A term appearing twice in one chunk contributes only one to document frequency.

Here “document frequency” counts **chunks**, even though the variable name says document. It does not count original source files. `1 + len(chunks)` and `1 + frequency` in the next calculation provide smoothing.

> **Remember:** Counter maps each item to its frequency.

### Exercise

Which counts the total tokens: len(counts) or sum(counts.values())?

<details>
<summary>Show answer</summary>

sum(counts.values()) gives 3 tokens. len(counts) gives 2 distinct terms.

</details>

 [← Previous](#chapter-14) · [All lessons](#lessons) · [Next →](#chapter-16)

---

<a id="chapter-16"></a>

## 16. Comprehensions and generators

[expression for item in items] builds a list.

### Try it locally: Build and consume values

```python
words = ["Python", "Notes"]
lowercase = [word.lower() for word in words]
lengths = (len(word) for word in words)
print(lowercase)
print(sum(lengths))
```

**Output**

```text
['python', 'notes']
11
```

### Example explained

1. The list contains two strings.
2. The square-bracket comprehension calls lower on each string and collects both results.
3. The parenthesized generator describes how to supply each word’s length when requested.
4. `sum(lengths)` consumes lengths 6 and 5 and returns 11. The generator is then exhausted.

### In this project

**Source:** src/search.py · index construction and score calculation

The following is a project excerpt or teaching diagram. Read it alongside the explanation; it may depend on surrounding code.

```python
# List comprehension: build all results now.
[Counter(tokenize(chunk.text)) for chunk in chunks]

# Dictionary comprehension: build term → weight entries.
{term: math.log((1 + len(chunks)) / (1 + frequency)) + 1
 for term, frequency in document_frequency.items()}

# Generator expression: supply values as they are consumed.
(term for counts in self.term_counts for term in counts.keys())
```

A **comprehension** is a compact way to transform an iterable. Read `[Counter(tokenize(chunk.text)) for chunk in chunks]` as “for every chunk, tokenize its text, count the tokens, and collect the resulting Counter.”

### Reading the project code

The dictionary comprehension unpacks each `.items()` pair into `term` and `frequency`, computes a weight, and stores it under that term.

A **generator expression** supplies values on demand rather than constructing a whole list. The nested form is read left to right: for each `counts`, then for each `term` in its keys, produce `term`. If a generator is the only argument of a call, Python permits omitting its own surrounding parentheses, which is why `Counter(term for ...)` works.

### A closer look

The score uses `sum(expression for term in matched_terms)`. Tests use `all(chunk.source == "notes/example.txt" for chunk in chunks)`. `sum` adds supplied numbers; `all` is true if every supplied condition is true (including when there are no items). No `yield` statement or custom generator function appears here.

> **Remember:** [expression for item in items] builds a list.

### Exercise

Which expression creates a list immediately?

<details>
<summary>Show answer</summary>

The square-bracket comprehension. The generator supplies lengths as sum consumes them.

</details>

 [← Previous](#chapter-15) · [All lessons](#lessons) · [Next →](#chapter-17)

---

<a id="chapter-17"></a>

## 17. Arithmetic and the search score

& finds shared terms.

### Try it locally: Calculate a score

```python
from src.models import DocumentChunk
from src.search import KeywordRetriever

chunks = [DocumentChunk("a", 1, "python python notes"),
          DocumentChunk("b", 1, "notes only")]
result = KeywordRetriever(chunks).search("python")[0]
print(f"{result.score:.3f}")
```

**Output**

```text
1.623
```

### Example explained

1. Create two passages so the search can compare word frequencies across them.
2. Build a KeywordRetriever and search for python.
3. Only passage a contains python, so `[0]` selects that result.
4. The f-string displays its stored score rounded to three decimal places. The project formula is explained below.

### In this project

**Source:** src/search.py · KeywordRetriever.search

The following is a project excerpt or teaching diagram. Read it alongside the explanation; it may depend on surrounding code.

```python
matched_terms = query_terms & counts.keys()
score = sum(
    min(counts[term], 3) * self.inverse_document_frequency.get(term, 1.0)
    for term in matched_terms
) / math.sqrt(sum(counts.values()))
```

`&` here is set intersection: only terms found in both the query set and the chunk's keys remain. It is not the Boolean keyword `and`. An empty intersection causes `continue`, so only matching chunks reach the score formula.

### Reading the project code

Python arithmetic here uses `+` for addition, `-` for subtraction or negation, `*` for multiplication, and `/` for division. Division produces a float. Parentheses group calculations; function-call parentheses invoke functions. `math.log` is the natural logarithm; `math.sqrt` is square root. `min(counts[term], 3)` caps repeated matches.

For a term, the weight is `log((1 + number_of_chunks) / (1 + chunks_containing_term)) + 1`. Sum the capped count times weight for each matching term, then divide by the square root of the chunk's retained-token count. A positive match guarantees at least one token, so that denominator is nonzero.

### A closer look

**Worked example:** two chunks contain `"python python notes"` and `"notes only"`. For query `"python"`, its weight is `log(3/2) + 1 ≈ 1.405465`. The first chunk scores `2 × 1.405465 / sqrt(3) ≈ 1.622891`, displayed as `1.623`. The other chunk is omitted. This is a TF-IDF-inspired score, not a probability or percentage confidence.

> **Remember:** & finds shared terms.

### Exercise

Is 1.623 a probability?

<details>
<summary>Show answer</summary>

No. It is a relative ranking score, not a confidence percentage.

</details>

 [← Previous](#chapter-16) · [All lessons](#lessons) · [Next →](#chapter-18)

---

<a id="chapter-18"></a>

## 18. Sorting, lambdas, and result limits

lambda defines a small unnamed function.

### Try it locally: Sort by a key

```python
scores = [("b.txt", 2.0), ("a.txt", 2.0), ("c.txt", 3.0)]
ranked = sorted(scores, key=lambda item: (-item[1], item[0]))
print(ranked[:2])
```

**Output**

```text
[('c.txt', 3.0), ('a.txt', 2.0)]
```

### Example explained

1. Each tuple holds a filename and its score.
2. The lambda gives sorted a two-part key: negative score first, filename second.
3. A score of 3 becomes -3, which sorts before -2. Equal scores fall through to filename order.
4. `ranked[:2]` takes the first two results without changing the original scores list.

### In this project

**Source:** src/search.py · end of KeywordRetriever.search

The following is a project excerpt or teaching diagram. Read it alongside the explanation; it may depend on surrounding code.

```python
return sorted(
    results,
    key=lambda result: (
        -result.score,
        result.chunk.source,
        result.chunk.chunk_number,
    ),
)[:limit]
```

`sorted(results, key=...)` returns a new sorted list. The `key` argument accepts a function: Python calls it for each result to obtain its sorting value. `lambda result: (...)` defines that function inline, with one parameter and one expression.

### Reading the project code

Tuples compare element by element. Sorting is ascending by default, so a negative score makes the greatest original score come first. If scores tie, the source filename breaks the tie. If those also tie, the chunk number decides.

`[:limit]` selects the first `limit` entries from the sorted list. Earlier, `if limit <= 0: return []` ensures zero and negative limits return no results. Without that guard, a negative slice would mean “omit items from the end,” not “return nothing.” The filenames and chunk numbers make tie handling deliberate, although floating-point arithmetic can have tiny rounding differences.

> **Remember:** lambda defines a small unnamed function.

### Exercise

Why does a.txt come before b.txt?

<details>
<summary>Show answer</summary>

Their scores tie, so the next tuple element, the filename, decides their order.

</details>

 [← Previous](#chapter-17) · [All lessons](#lessons) · [Next →](#chapter-19)

---

<a id="chapter-19"></a>

## 19. Command-line arguments and execution

argparse converts command text into values.

### Try it locally: Parse command options

```python
from src.cli import build_parser

args = build_parser().parse_args(["--verbose", "search", "python", "--limit", "2"])
print(args.verbose)
print(args.query)
print(args.limit)
```

**Output**

```text
True
python
2
```

### Example explained

1. `build_parser()` creates the parser configured by the project.
2. Passing a list to parse_args lets this example supply command-line words directly.
3. `--verbose` turns on a flag; search selects the subcommand; python is the query.
4. `--limit 2` is converted to an integer. The print calls read the resulting attributes.

### In this project

**Source:** src/cli.py · build_parser, main, and module guard

The following is a project excerpt or teaching diagram. Read it alongside the explanation; it may depend on surrounding code.

```python
parser.add_argument("--documents", type=Path, default=Path("documents"))
parser.add_argument("--verbose", action="store_true")
args = build_parser().parse_args()

if __name__ == "__main__":
    raise SystemExit(main())
```

`argparse.ArgumentParser` creates a parser object. `add_argument` configures an option; `type=Path` and `type=int` pass callable objects for conversion, rather than calling them at that moment. Defaults apply when options are absent. `action="store_true"` makes `--verbose` a flag that is false until supplied.

### Reading the project code

`add_subparsers(dest="command", required=True)` requires a subcommand and records its name in `args.command`. `add_parser("search")` defines the search subcommand. Its positional `query` is required; `--limit` defaults to three and `--retriever` defaults to `keyword`. `--model-cache` and `--offline` are options for semantic and hybrid modes. `parse_args()` reads command-line arguments and returns an object whose attributes include `args.documents`, `args.chunk_size`, and `args.query`. Hyphens in option names become underscores in attribute names.

`__name__` is set by Python. It is `"__main__"` when the module runs as the entry point and normally `"src.cli"` when imported. The guard prevents a simple import from launching the CLI. `main()` returns an integer; `raise SystemExit(main())` passes that value to the process exit mechanism. Zero means success; the no-documents branch returns one. No matches still returns zero. Expected semantic model/dependency errors return one; incompatible CLI options return two. `main()` performs the cross-option check after parsing, so calling `parse_args()` alone does not run that validation.

### A closer look

Example shell command: `python -m src.cli --chunk-size 80 --overlap 15 search "testing Python" --limit 2`. Global settings go before `search`; query settings go after it. Shell quotes keep a multiword query together; they are not Python string syntax being executed here.

> **Remember:** argparse converts command text into values.

### Exercise

Where does --verbose go relative to search?

<details>
<summary>Show answer</summary>

Before search, because it belongs to the main parser.

</details>

 [← Previous](#chapter-18) · [All lessons](#lessons) · [Next →](#chapter-20)

---

<a id="chapter-20"></a>

## 20. Printing, formatting, and logging

f-strings insert expression values inside braces.

### Try it locally: Format a number

```python
score = 1.622891
print(f"Score: {score:.3f}")
print(score)
```

**Output**

```text
Score: 1.623
1.622891
```

### Example explained

1. Assign a decimal number to score.
2. The f prefix allows the braces to contain a Python expression.
3. Inside the braces, `:.3f` requests three digits after the decimal point.
4. The final print displays the original value, showing that formatting did not change it.

### In this project

**Source:** src/cli.py · output; src/loader.py · LOGGER

The following is a project excerpt or teaching diagram. Read it alongside the explanation; it may depend on surrounding code.

```python
print(f"{index}. [{result.score:.3f}] {chunk.source} (chunk {chunk.chunk_number})")
print(f"   {chunk.text}")

LOGGER = logging.getLogger(__name__)
LOGGER.info("Loaded %d documents from %s", len(documents), directory)
```

A string prefixed with `f` is an **f-string**. Expressions inside `{...}` are evaluated and inserted into the string. `:.3f` formats a floating-point number with three digits after the decimal point; it changes its displayed form, not the stored score. `print` normally adds a newline.

### Reading the project code

`logging.getLogger(__name__)` gives the loader a logger named for its module. `LOGGER.debug` records per-file detail and `LOGGER.info` records a summary. The CLI selects DEBUG when verbose, otherwise INFO. Thus INFO summaries can appear even without `--verbose`.

Logging's `"Loaded %d documents from %s"` uses logging placeholders: `%d` formats an integer and `%s` formats a string representation, using the separately supplied arguments. The configuration format `"%(levelname)s: %(message)s"` uses named logging fields. These are different from f-string braces. By default, logging's stream handler writes to standard error, while `print` writes to standard output.

> **Remember:** f-strings insert expression values inside braces.

### Exercise

Did formatting change the value stored in score?

<details>
<summary>Show answer</summary>

No. It changes only the displayed text.

</details>

 [← Previous](#chapter-19) · [All lessons](#lessons) · [Next →](#chapter-21)

---

<a id="chapter-21"></a>

## 21. Exceptions and context managers

raise signals an exceptional condition.

### Try it locally: Expect an exception

```python
import pytest
from src.chunker import chunk_document
from src.models import Document

with pytest.raises(ValueError):
    chunk_document(Document("note.txt", "hello"), chunk_size=3, overlap=3)
print("Expected error confirmed")
```

**Output**

```text
Expected error confirmed
```

### Example explained

1. Import pytest and the project objects needed for the call.
2. `with pytest.raises(ValueError):` starts a block that expects a ValueError.
3. The call supplies an overlap equal to its chunk size. The chunker rejects it.
4. Pytest catches the expected exception, and execution continues to the print. If no ValueError were raised, the check would fail.

### In this project

**Source:** src/chunker.py · src/models.py · tests/test_chunker.py

The following is a project excerpt or teaching diagram. Read it alongside the explanation; it may depend on surrounding code.

```python
if chunk_size <= 0:
    raise ValueError("chunk_size must be greater than zero")

with pytest.raises(ValueError):
    chunk_document(Document("note.txt", "text"), chunk_size=3, overlap=3)
```

An **exception** interrupts normal execution. The chunker raises `ValueError` for a nonpositive size or overlap outside `0 <= overlap < chunk_size`. The base retriever raises `NotImplementedError` when its placeholder method is called. `SystemExit` is the explicit exit mechanism used by the CLI.

### Reading the project code

There is no application `try/except` block in this project. Invalid numeric chunk settings therefore produce an uncaught error rather than a custom CLI message. Argparse handles its own parsing errors, such as a non-integer `--limit`.

`with` invokes a **context manager** around an indented block. In tests, `pytest.raises(ValueError)` expects an exception of that type. It catches the expected error so the test can pass; if no error occurs, or an unexpected type occurs, the test fails. The test shown checks overlap equal to the chunk size, which would otherwise give a zero step.

> **Remember:** raise signals an exceptional condition.

### Exercise

Why is overlap=3 invalid when chunk_size=3?

<details>
<summary>Show answer</summary>

The step would be zero, so the windows would not advance.

</details>

 [← Previous](#chapter-20) · [All lessons](#lessons) · [Next →](#chapter-22)

---

<a id="chapter-22"></a>

## 22. Tests, fixtures, and assertions

pytest discovers test_ functions.

### Try it locally: Check an expectation

```python
from src.search import tokenize

assert tokenize("PYTHON!") == ["python"]
print("Check passed")
```

**Output**

```text
Check passed
```

### Example explained

1. Call tokenize with uppercase text and punctuation.
2. `== ["python"]` compares its result with the expected list.
3. `assert` checks that the comparison is true.
4. Because it is true, execution reaches print. A false assertion would stop the normal path with AssertionError.

### In this project

**Source:** tests/test_loader.py · tests/test_chunker.py · tests/test_search.py

The following is a project excerpt or teaching diagram. Read it alongside the explanation; it may depend on surrounding code.

```python
def test_loader_finds_supported_files_recursively(tmp_path):
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "note.md").write_text("hello", encoding="utf-8")
    documents = load_documents(tmp_path)
    assert [(d.source, d.text) for d in documents] == [("nested/note.md", "hello")]
```

This shortened loader example omits the unsupported-file setup; the complete test also writes `ignore.csv` and checks it is excluded. Pytest finds files and functions named `test_...`. An `assert condition` fails with `AssertionError` when the condition is false; pytest reports the failure with useful detail.

### Reading the project code

`tmp_path` is a **fixture**: pytest sees that parameter name and supplies a temporary `Path` for that test. It is not a built-in Python keyword, and callers outside pytest do not receive it automatically.

The tests use list comprehensions to collect text, chunk numbers, or `(source, text)` tuples. `all(...)` checks that every chunk retains the expected source. Search tests check the result count, order, and the empty-query case. The project currently runs 122 default cases across nine test files, plus five embedding integration cases and four generation cases in separate files.

### Where the tests live

A **unit test** gives a small piece of code known inputs and checks the expected result. For example, the hybrid tests supply prepared rankings and check exact reciprocal-rank scores. Fake encoders supply controlled vectors without loading a model. These checks establish behavior; they cannot establish that real questions retrieve useful evidence.

The current suite has **122 default test cases** and **5 separately selected embedding integration cases**. Four additional generation cases exercise local Ollama; [the results report](ai/rag-answer-results.md) retains a known quality failure. A parametrized test runs the same function with several inputs, so cases and functions are different counts. Embedding integration checks use the actual cached model and block all networking. Generation checks permit the local runtime connection while blocking external traffic. The separate 23-question evaluation measures retrieval quality against unchanged source-and-evidence labels: hybrid Hit@3 is 75%, versus semantic's 85%, even though the implementation tests pass.

| Test file | What it verifies |
| --- | --- |
| [test_loader.py](tests/test_loader.py) | Supported files, recursive loading, original text and source paths |
| [test_chunker.py](tests/test_chunker.py) | Overlap, source metadata, and invalid settings |
| [test_search.py](tests/test_search.py) | Keyword ranking, stop words, empty queries, and result limits |
| [test_semantic.py](tests/test_semantic.py) | Controlled vectors, model adapter behavior, index reuse, and errors |
| [test_hybrid.py](tests/test_hybrid.py) | Fusion arithmetic, identities, ties, candidate depth, and failures |
| [test_cli.py](tests/test_cli.py) | Mode selection, arguments, output, diagnostics, and exit statuses |
| [test_semantic_integration.py](tests/test_semantic_integration.py) | Actual model retrieval and complete/missing offline caches |

### Running and reading test results

Run from the project root with the existing development environments:

```bash
# Default checks: no model dependency or download needed.
.venv/bin/python -m pytest -v
# Focus on the hybrid behavior.
.venv/bin/python -m pytest tests/test_hybrid.py -v
# Actual model checks: requires the semantic environment and populated cache.
.venv-semantic/bin/python -m pytest -m integration -v
# Quality measurement: writes the separate hybrid evaluation reports.
.venv-semantic/bin/python -m evaluations.run_retrieval
```

`-m pytest` runs pytest through the selected Python interpreter; `-v` lists individual cases. Pytest's `-m integration` selects the integration marker. Without that selection, `pyproject.toml` excludes model checks. `PASSED` means an expectation held, `FAILED` means it did not, and `deselected` means a case was intentionally outside that run. A missing required model cache fails an explicit integration run; it is not silently skipped.

A test usually has three steps: **arrange** inputs, **act** by calling the code, then **assert** the expected result. In the loader excerpt, writing the note arranges the input, `load_documents(tmp_path)` performs the action, and the final assertion checks both the path and text. `monkeypatch` temporarily replaces a dependency; `capsys` captures printed output; `caplog` captures logs. Pytest restores these fixtures after each test so cases remain independent.

To read a failure, start with the test name and failed assertion, then compare the expected and actual values. Re-run that case with a selector such as `tests/test_hybrid.py::test_worked_example_uses_order_not_scores`. Investigate the behavior before changing an expectation; weakening a test merely to make it green can hide a bug.

### A closer look

Run `python -m pytest` with development dependencies installed. Assertions belong to tests here. They should not replace essential user-input checks: Python's optimized mode can omit assert statements, whereas explicit `if ...: raise ...` validation remains.

> **Remember:** pytest discovers test_ functions.

### Exercise

What happens if an assertion is false?

<details>
<summary>Show answer</summary>

Python raises AssertionError, and pytest reports the test as failed.

</details>

 [← Previous](#chapter-21) · [All lessons](#lessons) · [Next →](#chapter-23)

---

<a id="chapter-23"></a>

## 23. Running and tracing the project

Use Python 3.10 or newer.

### Try it locally: Trace the full workflow

```python
from src.models import Document
from src.chunker import chunk_documents
from src.search import KeywordRetriever

notes = [Document("note.txt", "python notes are useful")]
chunks = chunk_documents(notes)
results = KeywordRetriever(chunks).search("python")
print(results[0].chunk.text)
```

**Output**

```text
python notes are useful
```

### Example explained

1. Create a list containing one Document, representing a loaded note.
2. `chunk_documents(notes)` converts documents into a list of searchable passages.
3. `KeywordRetriever(chunks).search("python")` prepares the index and searches it.
4. Select the first result, access its chunk, and print that chunk’s text. This follows the same data flow as the CLI.

### In this project

**Source:** README.md · pyproject.toml · src/cli.py

The following is a project excerpt or teaching diagram. Read it alongside the explanation; it may depend on surrounding code.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m src.cli search "Python" --limit 2
python -m pytest
```

These are **shell commands**, not Python statements. They follow the project's macOS/Linux setup. The virtual environment isolates installed packages. `python -m pip` runs pip through the selected interpreter. `-e` installs the local project in editable mode; `.[dev]` also installs its optional pytest dependency. The base keyword application has no external runtime dependencies. `.[semantic]` adds the optional local embedding stack; `.[dev,semantic]` installs both extras.

### Reading the project code

`pyproject.toml` is TOML configuration, not Python source. `[build-system]` selects setuptools; `[project]` declares metadata and Python requirements; `[project.optional-dependencies]` defines `dev` and `semantic`; `[tool.pytest.ini_options]` sets test discovery and import paths; `[tool.setuptools]` includes the `src` package. `README.md`, the notes, this guide, and the narration are Markdown; the slideshow uses HTML, CSS, and JavaScript.

To trace a search, follow `args.documents` into `load_documents`, its `Document` objects into `chunk_documents`, their `DocumentChunk` objects into the selected retriever, and the returned `SearchResult` objects into the print loop.

### A closer look

**Practice:** predict the output of `tokenize("Python_3!")`; predict the number of chunks for seven words with size four and overlap one; explain why repeating a query term does not boost its score. Answers: `['python', '3']`; three chunks; query tokens are converted to a set.

> **Remember:** Use Python 3.10 or newer.

### Exercise

Which objects connect chunk_documents to KeywordRetriever?

<details>
<summary>Show answer</summary>

DocumentChunk objects, collected in a list.

</details>

 [← Previous](#chapter-22) · [All lessons](#lessons) · [Next →](#chapter-24)

---

<a id="chapter-24"></a>

## 24. Stop-word filtering with frozenset

A stop word is a word the search deliberately ignores. This project excludes a fixed list of 26 common English words. The full vocabulary and its limitations are in [the README](README.md#stop-word-filtering).

### Try it locally: Keep only searchable words

```python
from src.search import STOP_WORDS, tokenize

# Membership checks ask whether an entire token is in the immutable set.
print(isinstance(STOP_WORDS, frozenset))
print("the" in STOP_WORDS)
# Lowercasing happens before filtering; substrings are never removed.
print(tokenize("THE theory is useful"))
print(tokenize("not never no python python 123"))
# An empty list is a valid result, not an error.
print(tokenize("the is how"))
```

**Output**

```text
True
True
['theory', 'useful']
['not', 'never', 'no', 'python', 'python', '123']
[]
```

### Reading the project code

A `frozenset` is a set that cannot be changed in place. It supports fast membership checks such as `term in STOP_WORDS`, but has no `add` or `remove` methods. Uppercase naming marks `STOP_WORDS` as a constant by convention; it does not itself enforce immutability.

The list comprehension in `tokenize` reads: “for each normalized token, keep it if it is not a stop word.” Unlike converting the result to a set, this preserves order and repeated tokens for passage scoring. Query deduplication happens separately in `search`.

```python
# Shortened project excerpt: TOKEN_PATTERN and STOP_WORDS are defined above it.
return [term for term in TOKEN_PATTERN.findall(text.lower()) if term not in STOP_WORDS]
```

Both passages and queries call the same function. Counts and the square-root length penalty use retained tokens. Original passage text, source, and chunk number are unchanged, and chunking still uses original whitespace words. All original chunks contribute to the IDF corpus size, even ones with no searchable tokens. The no-match guard skips such chunks before division, preventing division by zero.

### Check the behavior with assertions

```python
from src.models import DocumentChunk
from src.search import KeywordRetriever

# The filler passage shares only excluded words with the question.
chunks = [
    DocumentChunk("filler.txt", 1, "how is how is how is"),
    DocumentChunk("retrieval.md", 1, "retrieval finds useful passages"),
]
retriever = KeywordRetriever(chunks)
assert retriever.search("the is how") == []
# Dataclass equality compares both the original passage metadata and score.
assert retriever.search("how is retrieval") == retriever.search("retrieval")
print([result.chunk.source for result in retriever.search("how is retrieval")])
```

**Output**

```text
['retrieval.md']
```

Before filtering, the filler scored 3.442672 and ranked first. After filtering, only the retrieval passage matches, at 0.702733. See the [measured comparison](README.md#before-and-after-comparison). The stop-word milestone had nine tests; current validation is 122 deterministic tests plus 5 embedding checks; local-generation outcomes are recorded separately.

### Exercise

Why does `theory` survive filtering while `THE` does not? Why keep `not`?

<details>
<summary>Show answer</summary>

The tokenizer lowercases first and compares whole tokens. `theory` is not in the exclusion set; `the` is. Negation can carry meaning, so `no`, `not`, and `never` remain. Keeping them does not give literal keyword matching an understanding of sentences. The fixed English list can still discard useful words in titles and has no override.

</details>


[← Previous](#chapter-23) · [All lessons](#lessons) · [Next →](#chapter-25)

<a id="chapter-25"></a>

## 25. Semantic search, vectors, and optional dependencies

An embedding is a list of numbers representing text. The model learns those numbers; we should not assume a coordinate directly means “bread” or “files.” Similar vector directions can identify paraphrases. This is a second retrieval method, selected with `--retriever semantic`; keyword mode remains the default.

### Try it locally: Normalize a vector

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

**Output**

```text
[0.6, 0.8]
0.6
```

### Example explained

1. Squaring the components and adding gives 25; its square root is length 5.
2. The list comprehension divides each component by 5, producing a unit vector.
3. `zip` pairs corresponding components of the passage and query.
4. Adding their products gives cosine similarity because both vectors have unit length. Same directions score 1, perpendicular directions 0, and opposite directions -1.

### Try it locally: Inject a fake encoder

```python
from src.models import DocumentChunk
from src.semantic import SemanticRetriever

class TeachingEncoder:
    """Known vectors teach ranking without downloading a model."""

    def encode(self, texts):
        """Return one vector per original text in the requested order."""
        vectors = {"save a copy": [1, 0], "bread rises": [0, 1], "recover files": [3, 0]}
        return [vectors[text] for text in texts]

chunks = [DocumentChunk("backup.md", 1, "save a copy"),
          DocumentChunk("bread.md", 1, "bread rises")]
# Supplying the encoder keeps optional model packages out of this example.
retriever = SemanticRetriever(chunks, encoder=TeachingEncoder())
for result in retriever.search("recover files", limit=2):
    print(result.chunk.source, result.score)
```

**Output**

```text
backup.md 1.0
bread.md 0.0
```

### Reading the project code

`Encoder` is a `Protocol`: it describes an object that has an `encode` method accepting texts and returning vectors. The real adapter and this teaching object satisfy that shape without needing the same parent class. Type hints describe the shape; runtime validation still checks vector counts, dimensions, finite values, and nonzero lengths.

Passing an encoder is **dependency injection**: supply the component the retriever needs instead of hard-coding a model inside every search. A fake teaches and tests ranking, but cannot prove that a real model recognizes paraphrases. That requires the separate integration comparison.

The retriever stores chunks in a tuple so changing the caller's list cannot scramble the index. Passage embeddings are computed once per instance; each query is encoded separately. Model files persist in a disk cache, but passage vectors are rebuilt by each CLI invocation.

### Optional packages and lazy loading

The import of Sentence Transformers is inside the model adapter's load method. Importing `src.semantic` alone uses only the standard library. Empty queries, empty collections, and nonpositive limits return without loading a model. Keeping the optional dependency behind this boundary lets the same base project run with only keyword search.

```bash
# Terminal commands, not Python statements; first search can download model assets.
python -m pip install -e '.[dev,semantic]'
python -m src.cli search "finding information" --retriever semantic
python -m src.cli search "finding information" --retriever semantic --offline
```

The default cache is `.cache/ask-my-notes/models`; `--model-cache PATH` selects another. Offline mode loads the pinned revision locally and fails with instructions if assets are missing. It does not silently switch to keyword search. In this workspace the optional stack lives in `.venv-semantic`; use its Python executable for the commands above.

### Model behavior and tests

The real model keeps original sentences, including stop words, and applies its own tokenizer. Its token limit can truncate text, so the adapter warns before encoding. Original text and source metadata still appear in results. Nonblank punctuation and stop-word-only questions are valid model inputs, unlike keyword filtering's empty-result behavior.

The current validation is **122 deterministic tests plus 5 embedding integration checks, with local-generation outcomes recorded separately**. Both predefined paraphrases ranked their expected passage first with semantic search; keyword mode missed them. The unrelated questions still returned neighbors. See [the measured comparison](ai/semantic-search-results.md) for scores and reproducible commands.

### Exercise

Can the fake encoder above prove the downloaded model understands “recover files”? Is a cosine of 0.6 a 60% probability that a passage answers the question?

<details>
<summary>Show answer</summary>

No to both. The fake proves vector handling and ordering for explicitly chosen inputs. The real model needs its own labeled checks. Cosine is a similarity measure, not calibrated answer confidence; even unrelated questions receive nearest passages because no relevance threshold exists.

</details>


### Trace a real semantic search

Use the workspace’s prepared environment and model cache:

```bash
# Keyword path: no optional model package is needed.
.venv/bin/python -m src.cli search "finding information" --retriever keyword
# Semantic path: the pinned model is already cached in this workspace.
.venv-semantic/bin/python -m src.cli search "finding information" --retriever semantic --offline
# Default tests use fakes; the explicit integration run uses the actual model.
.venv/bin/python -m pytest -q
.venv-semantic/bin/python -m pytest -m integration -s -q
```

On a fresh checkout, install `.[dev,semantic]` and run the semantic command without `--offline` once to download model assets. Offline mode is an explicit promise not to fetch missing files; an empty cache fails with setup guidance. Never remove `--offline` automatically after a failure.

Follow the values: parsed options select `SemanticRetriever`; original chunks are snapshotted; the first meaningful query loads the adapter and embeds passages; the query is encoded; valid vectors are normalized and compared; sorted `SearchResult` objects reach the unchanged print loop. A later query on the same retriever reuses passage vectors. Starting a new CLI process rebuilds that passage index, while reusing the model files on disk.

[← Previous](#chapter-24) · [All lessons](#lessons) · [Next →](#chapter-26)

---

<a id="chapter-26"></a>

## 26. Hybrid search with reciprocal ranks

Hybrid retrieval combines two ordered lists. We cannot add raw keyword and semantic scores because they mean different things. Instead, a passage receives `1 / (60 + rank)` from each list in which it appears. Ranks start at 1; absent passages contribute nothing.

### Try it locally: Fuse prepared rankings

```python
from src.hybrid import fuse_rankings
from src.models import DocumentChunk, SearchResult

# Identity comes from source and chunk number; raw scores are deliberately unrelated.
a = DocumentChunk("A", 1, "Passage A")
b = DocumentChunk("B", 1, "Passage B")
c = DocumentChunk("C", 1, "Passage C")
keyword = [SearchResult(a, 100), SearchResult(b, 20)]
semantic = [SearchResult(c, 0.9), SearchResult(a, 0.1)]
for result in fuse_rankings(keyword, semantic):
    print(result.chunk.source, f"{result.score:.6f}")
```

**Output**

```text
A 0.032522
C 0.016393
B 0.016129
```

### Example explained

1. `DocumentChunk` carries original text and a stable identity: source plus chunk number.
2. Each `SearchResult` list is already ranked. RRF uses its positions, ignoring the scores 100, 20, 0.9, and 0.1.
3. A appears first in keyword and second in semantic, receiving `1/61 + 1/62`.
4. C receives `1/61`, B `1/62`. The output is A, C, B. Changing raw scores without reordering the lists leaves fusion unchanged.

### Reading the project code

`enumerate(branch, start=1)` produces one-based `(rank, result)` pairs. A tuple `(source, chunk_number)` is a dictionary key because these values identify a passage within the snapshot. A separate `seen` set for each branch prevents repeated entries from voting twice. First positions are preserved; duplicates do not renumber later entries.

`setdefault(key, value)` inserts a default only when the key is absent, helping keep the first original chunk. Conflicting text for an existing identity raises `ValueError`; equal text at different identities is allowed. Contributions are collected in lists and added with `math.fsum`, which reduces floating-point summation error. Sorting uses full scores, then filename and chunk number, before taking the final slice.

### Candidate depth and composition

`HybridRetriever` creates and reuses a keyword retriever and a semantic retriever. This is **composition**: a class delegates parts of its work to other objects. Its constructor snapshots unique nonblank chunks. The keyword branch receives a private list; changing the caller's list cannot shift its stored counts. The semantic branch loads its model and caches passage vectors only when needed.

For N eligible chunks, both branches receive `limit=N`, regardless of the user's display limit. A passage below an individual top-one cutoff can rise after fusion. Using the full lists also means requesting one result gives the first result of requesting three. The fusion helper returns a `SearchResult` whose score is RRF, not cosine or keyword weight.

### Try it locally: See fusion hurt relevance

```python
from src.hybrid import fuse_rankings
from src.models import DocumentChunk, SearchResult

noise = SearchResult(DocumentChunk("noise.md", 1, "Weak literal match"), 1.0)
answer = SearchResult(DocumentChunk("answer.md", 1, "Relevant paraphrase"), 0.9)
# Semantic gets the answer right. Keyword's extra vote promotes the wrong passage.
semantic = [answer, noise]
print("semantic:", semantic[0].chunk.source)
print("hybrid:", fuse_rankings([noise], semantic)[0].chunk.source)
```

**Output**

```text
semantic: answer.md
hybrid: noise.md
```

The noise passage receives two contributions while the answer receives one. Correct arithmetic does not establish good relevance. On the existing 23-question evaluation, hybrid Hit@3 is 75%, keyword 75%, and semantic 85%. Hybrid improves one semantic miss and regresses on three semantic hits. [The report](evaluations/hybrid-results.md) preserves the labels and explains each outcome.

### Run the actual mode

```bash
.venv-semantic/bin/python -m src.cli search "finding information" --retriever hybrid --offline
```

Hybrid reuses the existing semantic extra, pinned model, cache directory, and offline flag. A fresh setup must populate that cache online first. No additional dependency is needed. Blank requests avoid branch searches; nonblank stop-word-only questions may still receive semantic contributions. A failed semantic branch aborts the search instead of returning partial keyword results.

### Exercise

Should changing raw scores without reordering the branch lists change the fused answer? Should identical text in different files be collapsed?

<details>
<summary>Show answer</summary>

No to both. RRF uses positions rather than raw scores. Identity is filename plus chunk number, so equal text in different files represents distinct passages. Repeated identities vote once per branch. Conflicting text for one identity is an error. A fused score is not a confidence probability, and display rounding must not affect ranking.

</details>

[← Previous](#chapter-25) · [All lessons](#lessons) · [Next →](#chapter-27)

---

<a id="chapter-27"></a>

## 27. Local answers, JSON, and generator protocols

`search` returns existing passages. `ask` adds a local generator that writes an answer from selected passages, then Python validates the response and displays citations. The default `ask` retriever is semantic, while `search` stays keyword. We can learn this workflow with a fake generator and no runtime or downloads.

### Try it locally: Answer with a fake generator

```python
from src.answering import answer_question, render_answer
from src.models import DocumentChunk
from src.search import KeywordRetriever

class DemoGenerator:
    # This fake tests plumbing; it does not understand the question.
    def generate(self, question, context):
        return '{"status":"answered","claims":[{"text":"Backups run Friday.","citations":["S1"]}]}'

notes = [DocumentChunk("backup.md", 1, "Backups run Friday.")]
answer = answer_question("When do backups run?", KeywordRetriever(notes), DemoGenerator())
print(render_answer(answer))
```

**Output**

```text
Backups run Friday. [S1]

Sources:
[S1] backup.md (chunk 1)
   Backups run Friday.
```

### Example explained

1. `KeywordRetriever(notes)` prepares a tiny collection; it returns the matching original chunk.
2. `answer_question` builds bounded evidence and assigns the passage the request-local ID S1.
3. `DemoGenerator` has the `generate(question, context)` method required by the `Generator` Protocol. It need not inherit from it: matching the required method shape is structural typing.
4. The fake returns a JSON string. `json.loads` turns it into Python dictionaries/lists; it does not execute the text as code. `json.dumps` performs the reverse conversion when building a request.
5. Validation checks status, claims, citation IDs, duplicate fields, and bounds. Frozen dataclasses hold the validated result.
6. Rendering adds the source name, chunk number, and original text from the application's context. The model does not supply those display paths.

### Try it locally: Reject an invented citation

```python
from src.answering import AnswerError, build_context, validate_answer
from src.models import DocumentChunk, SearchResult

context = build_context([SearchResult(DocumentChunk("note.md", 1, "A fact."), 1.0)])
raw = '{"status":"answered","claims":[{"text":"A fact.","citations":["S99"]}]}'
try:
    validate_answer(raw, context)
except AnswerError:
    print("Rejected an unknown citation")
```

**Output**

```text
Rejected an unknown citation
```

### Reading the project code

A `Protocol` describes what methods a collaborator must offer. This lets tests supply fakes while production uses `LocalGenerator`. The local adapter uses standard-library `http.client` to speak HTTP to Ollama on 127.0.0.1:11434. It does not need a Python Ollama SDK, API key, or hosted account. The separate Ollama process and model weights do need setup.

`with`/`finally` cleanup patterns keep resources bounded; the adapter closes its HTTP connection in `finally`, even on an error. `monotonic()` measures elapsed time without relying on wall-clock changes. Byte limits bound response reads. The constructor validates settings without connecting; only `generate` contacts the runtime. A model preflight verifies the name, manifest digest, local GGUF weights, and lack of remote metadata before sending a question.

`build_context` uses source/chunk tuples for identity. It serializes metadata and text, tests the character budget, and includes only complete passages. JSON escaping keeps quotes, newlines, and instruction-like text inside data fields. Character count is not token count; the adapter applies a conservative byte/token bound and reserves room for output. Notes are data, not instructions, but even a clear prompt cannot guarantee correct model behavior.

### Failure versus insufficient evidence

An empty retrieval result returns the fixed insufficient-evidence message without a model call. A valid model abstention also succeeds. Invalid citations, malformed JSON, unavailable runtime, missing weights, and timeouts raise `AnswerError`; the CLI prints a concise error and exits 1. Bad arguments exit 2. No retry, hosted fallback, or partial answer is emitted.

Known IDs prove provenance, not truth. A model can cite S1 yet misread it, omit a conflicting S2, or refuse a supported question. The fixed answer evaluation records these cases. The small model's injection-adjacent question remains a failed quality check, rather than weakening the expected result to claim success.

### Run the real local model

Follow [local setup](README.md#local-model-setup) first. In this workspace, use:

```bash
.venv-semantic/bin/python -m src.cli ask "How does retrieval work?" --retrieval-offline
# Base environment: no embedding dependency, but still requires local Ollama.
.venv/bin/python -m src.cli ask "How does retrieval work?" --retriever keyword
# Default tests use fakes; this explicit run uses installed local models.
.venv-semantic/bin/python -m pytest -m generation_integration -q
```

Ollama 0.34.3 runs pinned Qwen2.5 1.5B weights on this 8 GiB Mac. The embedding model and generation model are separate. Setup downloads about 986 MB of generation weights; answering never pulls them. The runtime is loopback-only with cloud disabled; generation releases its model after each answer. `--retrieval-offline` separately prevents embedding-network checks. The integration client and the server need separate network controls because they are separate processes.

### Exercise

If `validate_answer` accepts a citation, has it proved the model's claim is correct? Can the fake example prove the real model follows grounding instructions?

<details>
<summary>Show answer</summary>

No to both. Validation checks structure and citation membership. A fake proves the workflow behaves as specified. Real-model checks and manual comparison against original evidence measure factual support, completeness, and abstention.

</details>

[← Previous](#chapter-26) · [All lessons](#lessons) · [Source coverage](#source-coverage-index)

---

## Source coverage index

| File | What this guide explains | Chapters |
| --- | --- | --- |
| [src/answering.py](src/answering.py) | Protocol, frozen records, bounded JSON context, strict validation, citations | 11, 21–22, 27 |
| [src/local_generator.py](src/local_generator.py) | Local HTTP, deadlines, bytes, finally cleanup, model preflight, JSON schema | 19–22, 27 |
| [tests/test_answering.py](tests/test_answering.py), [test_local_generator.py](tests/test_local_generator.py), [test_ask_cli.py](tests/test_ask_cli.py) | Fake collaborators, transport failures, grounded-answer contracts | 22, 27 |
| [tests/test_generation_integration.py](tests/test_generation_integration.py) | Actual local models, loopback-only client networking, quality expectations | 22, 27 |
| [evaluations/run_answers.py](evaluations/run_answers.py) | Recording wrapper, hashes, observed versus expected answers | 27 |
| [src/__init__.py](src/__init__.py) | Package marker and module docstring | 2–3 |
| [src/models.py](src/models.py) | Imports, annotations, decorators, three dataclasses, base class, methods, exceptions | 2, 5–6, 11–12, 21 |
| [src/loader.py](src/loader.py) | Constants, Path, recursion, sorting, conditions, membership, continue, text methods, append, logging | 4, 7–9, 13, 20 |
| [src/chunker.py](src/chunker.py) | Functions, defaults, annotations, validation, arithmetic, ranges, enumerate, unpacking, slicing, break, append, extend, return | 3–10, 21 |
| [src/search.py](src/search.py) | Regex, inheritance, initializer, self, Counter, comprehensions, generators, dictionary methods, set intersection, math, zip, lambda, tuple keys, slices | 6–9, 12, 14–18, 24 |
| [src/semantic.py](src/semantic.py) | Protocol, injected encoder, lazy imports, tuple snapshot, vector validation, normalization, cosine, caching, and errors | 6–8, 11–12, 16–17, 21, 25 |
| [src/hybrid.py](src/hybrid.py) | Composition, tuple identities, dictionaries, setdefault, per-branch sets, one-based enumerate, fsum, full candidates, and errors | 7–9, 16–18, 21, 26 |
| [src/cli.py](src/cli.py) | argparse, callables as arguments, attributes, conditional expression, truthiness, f-strings, formatting, main guard, exit status | 2, 4–6, 8–9, 19–20 |
| [tests/test_chunker.py](tests/test_chunker.py) | Positional and keyword arguments, assertions, comprehensions, all, generator, with, pytest.raises | 5, 10, 16, 21–22 |
| [tests/test_loader.py](tests/test_loader.py) | Fixture parameter, Path / operator, mkdir, write_text, tuples, comprehension, equality | 7, 13, 22 |
| [tests/test_search.py](tests/test_search.py) | Lists of objects, constructor/method chaining, indexing, comparisons, empty lists and queries | 7–8, 10–12, 22 |
| [tests/test_semantic.py](tests/test_semantic.py) | Fake vectors, parametrization, monkeypatch, cache arguments, and truncation checks | 21–22, 25 |
| [tests/test_hybrid.py](tests/test_hybrid.py) | Prepared rank lists, fake encoders, stable snapshots, limit prefixes, and relevance regression | 21–22, 26 |
| [evaluations/run_retrieval.py](evaluations/run_retrieval.py) | Fixed labels, evidence phrases, metadata, per-query ranks, and report generation | 22–23, 26 |
| [tests/test_cli.py](tests/test_cli.py) | Argument validation, fake retriever, exit statuses, and captured output | 19–22, 25 |
| [tests/test_semantic_integration.py](tests/test_semantic_integration.py) | Integration marker, network-blocking yield fixture, and real-model comparison | 22–23, 25 |
| [tests/fixtures/semantic_cases.py](tests/fixtures/semantic_cases.py) | Predefined documents and expected source labels | 7, 11, 22, 25 |
| [pyproject.toml](pyproject.toml) | Python version, base runtime, optional dependency extras, integration marker, package/test settings; TOML rather than Python | 23, 25 |

## Quick syntax reference

| Syntax | Read it as |
| --- | --- |
| `x = value` / `a == b` | Assign a value / compare equality |
| `obj.name` / `obj.method()` | Read an attribute / call a method |
| `def f(x):` / `return x` | Define a function / send a result back |
| `x: str` / `-> int` | Expected value type / expected return type |
| `[]` / `{a, b}` / `{key: value}` / `(a, b)` | List / set / dictionary / tuple |
| `frozenset(values)` | Construct an immutable set for membership tests |
| `class Encoder(Protocol):` | Describe the methods an injected encoder must provide |
| `def f(x, *, cache=...):` | Require callers to pass cache by keyword |
| `enumerate(items, start=1)` | Pair each item with its one-based rank |
| `mapping.setdefault(key, default)` | Keep an existing value or insert a default |
| `math.fsum(values)` | Sum floating-point contributions accurately |
| `items[i]` / `items[a:b]` | One item / a slice with an exclusive end |
| `if`, `not`, `or`, `in`, `not in` | Conditions, negation, alternatives, membership |
| `for`, `continue`, `break` | Repeat, skip this iteration, stop the loop |
| `a & b` | Intersection for the set-like operands used here |
| `class Child(Parent):` / `self` | Inherit behavior / this instance |
| `@dataclass(frozen=True)` | Generate record behavior and prevent normal field reassignment |
| `[f(x) for x in xs]` | Build a list by transforming each item |
| `(f(x) for x in xs)` | Supply transformed items on demand |
| `lambda x: expression` | A small unnamed function |
| `f"{score:.3f}"` | Insert a number displayed to three decimal places |
| `r"pattern"` | Raw string literal |
| `raise Error(...)` / `with ...:` / `assert ...` | Signal an exception / manage a block / check an expectation |

## What you do not need yet

You do not need neural-network training, async/await, or a database for this milestone. The small local HTTP client is now part of the project and is explained in chapter 27. Semantic mode uses a pretrained neural network through an optional library and may fetch model assets online. The integration tests use a `yield` fixture to check for network attempts after a test finishes. The `...` body in `Encoder.encode` declares a Protocol method shape; concrete encoders provide the implementation. These are distinct from shortened teaching excerpts.

## Teaching reference

The way concepts are introduced and practiced is inspired by [W3Schools Python tutorials](https://www.w3schools.com/python/python_intro.asp): short topic sections, examples, and practice. Explanations and examples here are written for this repository.
