"""Tests for overlapping chunks and chunk-setting validation.

Contents:
    - ``test_chunker_overlaps_words_and_preserves_metadata`` checks windows.
    - ``test_chunker_rejects_invalid_overlap`` checks input validation.
"""

import pytest

from src.chunker import chunk_document
from src.models import Document


def test_chunker_overlaps_words_and_preserves_metadata():
    """Verify overlap, chunk numbering, and source preservation together."""
    # Seven words with a four-word window make the overlap visible.
    document = Document("notes/example.txt", "one two three four five six seven")

    chunks = chunk_document(document, chunk_size=4, overlap=1)

    # The second chunk starts with the final word of the first chunk.
    assert [chunk.text for chunk in chunks] == ["one two three four", "four five six seven", "seven"]
    assert [chunk.chunk_number for chunk in chunks] == [1, 2, 3]
    assert all(chunk.source == "notes/example.txt" for chunk in chunks)


def test_chunker_rejects_invalid_overlap():
    """Reject overlap equal to the full chunk size."""
    # Such a setting would make the window advance by zero words.
    with pytest.raises(ValueError):
        chunk_document(Document("note.txt", "text"), chunk_size=3, overlap=3)