"""Fixed evaluation labels chosen before running either retrieval method.

Contents:
    - ``DOCUMENTS``: six short, distinct English notes outside the sample corpus.
    - ``QUERIES``: exact matches, zero-keyword-overlap paraphrases, and no-answer cases.

Default chunking (120 words, overlap 20) leaves each note as a single chunk.
The unrelated queries deliberately have no expected source: nearest neighbors
must not be mistaken for evidence that the corpus contains an answer.
"""

from src.models import Document

DOCUMENTS = [
    Document("backup.md", "Save duplicate copies of important files on an external drive to restore lost data."),
    Document("bread.md", "Bread dough rises when yeast ferments sugar and releases carbon dioxide bubbles."),
    Document("plants.md", "Water houseplants when the soil feels dry. Place the pot near a sunny window."),
    Document("cycling.md", "A bicycle helmet protects the rider's head during a fall. Check tire pressure before riding."),
    Document("retrieval.md", "Retrieval ranks relevant passages from a collection of documents to help answer questions."),
    Document("sleep.md", "A consistent bedtime and a dark quiet bedroom can support restful sleep."),
]

# None marks an intentionally unanswerable query. The two paraphrases share no
# retained keyword tokens with their expected passage; labels are not tuned to scores.
QUERIES = [
    ("exact", "external drive restore lost data", "backup.md"),
    ("exact", "yeast ferments sugar", "bread.md"),
    ("paraphrase", "How can I recover deleted computer documents?", "backup.md"),
    ("paraphrase", "Why does a loaf expand during baking?", "bread.md"),
    ("unrelated", "What is the orbital period of Neptune?", None),
    ("unrelated", "Who won the 1998 football World Cup?", None),
]
