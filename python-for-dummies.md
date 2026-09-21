# Python for Dummies: Ask My Notes

Learn Python one example at a time, using the code in Ask My Notes.

**Companions:** [Presenter script](python-for-dummies-script.md) · [HTML slideshow](python-for-dummies-slideshow.html)

Read the chapters in order for a first lesson, or use the coverage index at the end while reading source code. Every chapter has the same number as its slide and narration segment. Code with comments describing output is illustrative; shortened excerpts are identified. The pipeline arrows and terminal commands are not Python source.

## How to use this tutorial

Start with the short explanation. Run the small example, compare your output, then try the exercise. Read **In this project** to connect the idea to the real application.

**Before you start:** use Python 3.10 or newer. From the project root, activate the existing environment with `source .venv/bin/activate`. If it is not configured yet, follow [the setup instructions](README.md#install). Copy each complete **Try it locally** example into a temporary `.py` file in the project root and run it with `python filename.py`. Each example includes its own imports. Chapter 21 also needs the project's `pytest` development dependency. The HTML deck shows expected output; it does not execute Python in the browser.

**Learning path:** basics (1–6) → collections and control flow (7–10) → objects and files (11–13) → search logic (14–18) → CLI and tests (19–23).

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
          → KeywordRetriever → search → print
```

Ask My Notes searches local `.md` and `.txt` files. It returns passages and their filenames; it does not generate answers or call an AI model. The arrows above describe the program, not executable Python.

### Reading the project code

A **program** is a set of instructions. A **value** is a piece of data, such as text or a number. A **variable** is a name that refers to a value. A **function** groups instructions you can reuse. An **object** bundles data and behavior. You will meet each idea in the order the application needs it.

The application uses Python's standard library. Tests additionally use `pytest`. This guide covers all language constructs in the project's own Python files, including the tests; it does not attempt to teach the internals of Python or installed dependencies.

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
    return TOKEN_PATTERN.findall(text.lower())
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
    return TOKEN_PATTERN.findall(text.lower())

# tokenize("Python 3.10!")
# → ["python", "3", "10"]
```

A **regular expression** is a small pattern language for matching text. `[a-z0-9]` means one lowercase ASCII letter or digit; `+` means one or more consecutive matches. `r"..."` is a raw string literal, which preserves backslashes for patterns that use them; this particular pattern has no backslashes.

### Reading the project code

The tokenizer lowercases first, then finds matches. Punctuation and spaces separate terms. An underscore is not included. Non-ASCII letters are not included by this pattern either. `"don't"` becomes `['don', 't']`. `retrieval` and `retrieving` remain different words: there is no stemming or synonym handling.

Chunking uses whitespace words; scoring uses these regex tokens. Those are different boundaries. A chunk containing only punctuation may contain no tokens and therefore cannot match a query.

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

For a term, the weight is `log((1 + number_of_chunks) / (1 + chunks_containing_term)) + 1`. Sum the capped count times weight for each matching term, then divide by the square root of the chunk's total token count. A positive match guarantees at least one token, so that denominator is nonzero.

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

`add_subparsers(dest="command", required=True)` requires a subcommand and records its name in `args.command`. `add_parser("search")` defines the search subcommand. Its positional `query` is required; `--limit` defaults to three. `parse_args()` reads command-line arguments and returns an object whose attributes include `args.documents`, `args.chunk_size`, and `args.query`. Hyphens in option names become underscores in attribute names.

`__name__` is set by Python. It is `"__main__"` when the module runs as the entry point and normally `"src.cli"` when imported. The guard prevents a simple import from launching the CLI. `main()` returns an integer; `raise SystemExit(main())` passes that value to the process exit mechanism. Zero means success; the no-documents branch returns one. No matches still returns zero.

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

The tests use list comprehensions to collect text, chunk numbers, or `(source, text)` tuples. `all(...)` checks that every chunk retains the expected source. Search tests check the result count, order, and the empty-query case. The project currently has five test functions across three files.

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

These are **shell commands**, not Python statements. They follow the project's macOS/Linux setup. The virtual environment isolates installed packages. `python -m pip` runs pip through the selected interpreter. `-e` installs the local project in editable mode; `.[dev]` also installs its optional pytest dependency. The application has no external runtime dependencies.

### Reading the project code

`pyproject.toml` is TOML configuration, not Python source. `[build-system]` selects setuptools; `[project]` declares metadata and Python requirements; `[project.optional-dependencies]` defines `dev`; `[tool.pytest.ini_options]` sets test discovery and import paths; `[tool.setuptools]` includes the `src` package. `README.md`, the notes, this guide, and the narration are Markdown; the slideshow uses HTML, CSS, and JavaScript.

To trace a search, follow `args.documents` into `load_documents`, its `Document` objects into `chunk_documents`, their `DocumentChunk` objects into `KeywordRetriever`, and the returned `SearchResult` objects into the print loop.

### A closer look

**Practice:** predict the output of `tokenize("Python_3!")`; predict the number of chunks for seven words with size four and overlap one; explain why repeating a query term does not boost its score. Answers: `['python', '3']`; three chunks; query tokens are converted to a set.

> **Remember:** Use Python 3.10 or newer.

### Exercise

Which objects connect chunk_documents to KeywordRetriever?

<details>
<summary>Show answer</summary>

DocumentChunk objects, collected in a list.

</details>

 [← Previous](#chapter-22) · [All lessons](#lessons)

---

## Source coverage index

| File | What this guide explains | Chapters |
| --- | --- | --- |
| [src/__init__.py](src/__init__.py) | Package marker and module docstring | 2–3 |
| [src/models.py](src/models.py) | Imports, annotations, decorators, three dataclasses, base class, methods, exceptions | 2, 5–6, 11–12, 21 |
| [src/loader.py](src/loader.py) | Constants, Path, recursion, sorting, conditions, membership, continue, text methods, append, logging | 4, 7–9, 13, 20 |
| [src/chunker.py](src/chunker.py) | Functions, defaults, annotations, validation, arithmetic, ranges, enumerate, unpacking, slicing, break, append, extend, return | 3–10, 21 |
| [src/search.py](src/search.py) | Regex, inheritance, initializer, self, Counter, comprehensions, generators, dictionary methods, set intersection, math, zip, lambda, tuple keys, slices | 6–9, 12, 14–18 |
| [src/cli.py](src/cli.py) | argparse, callables as arguments, attributes, conditional expression, truthiness, f-strings, formatting, main guard, exit status | 2, 4–6, 8–9, 19–20 |
| [tests/test_chunker.py](tests/test_chunker.py) | Positional and keyword arguments, assertions, comprehensions, all, generator, with, pytest.raises | 5, 10, 16, 21–22 |
| [tests/test_loader.py](tests/test_loader.py) | Fixture parameter, Path / operator, mkdir, write_text, tuples, comprehension, equality | 7, 13, 22 |
| [tests/test_search.py](tests/test_search.py) | Lists of objects, constructor/method chaining, indexing, comparisons, empty lists and queries | 7–8, 10–12, 22 |
| [pyproject.toml](pyproject.toml) | Python version, standard-library runtime, development dependency, package/test settings; TOML rather than Python | 23 |

## Quick syntax reference

| Syntax | Read it as |
| --- | --- |
| `x = value` / `a == b` | Assign a value / compare equality |
| `obj.name` / `obj.method()` | Read an attribute / call a method |
| `def f(x):` / `return x` | Define a function / send a result back |
| `x: str` / `-> int` | Expected value type / expected return type |
| `[]` / `{a, b}` / `{key: value}` / `(a, b)` | List / set / dictionary / tuple |
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

The current source does not use async/await, threading, custom decorators, `yield` functions, database access, HTTP APIs, neural networks, or an LLM SDK. Learn these when a later milestone introduces them. The `...` omission marker in this guide does not appear as a function body in the application.

## Teaching reference

The way concepts are introduced and practiced is inspired by [W3Schools Python tutorials](https://www.w3schools.com/python/python_intro.asp): short topic sections, examples, and practice. Explanations and examples here are written for this repository.
