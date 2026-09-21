"""Split documents into overlapping word-based chunks.

Contents:
    - ``chunk_document`` for one document and its validation rules.
    - ``chunk_documents`` for applying the same settings to a collection.
"""

from .models import Document, DocumentChunk


def chunk_document(document: Document, chunk_size: int = 120, overlap: int = 20) -> list[DocumentChunk]:
    """Create chunks of at most ``chunk_size`` words with overlap between them.

    The input is converted to words first, then each window advances by
    ``chunk_size - overlap``. This preserves context between neighboring
    chunks while retaining the source metadata on every result.
    """
    # Invalid settings would otherwise create an infinite loop or surprising
    # empty output, so reject them before doing any work.
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be between zero and chunk_size - 1")

    # split() gives a simple word-based boundary and removes repeated spacing.
    words = document.text.split()
    chunks: list[DocumentChunk] = []
    step = chunk_size - overlap
    # enumerate supplies the human-friendly one-based chunk number.
    for chunk_number, start in enumerate(range(0, len(words), step), start=1):
        chunk_words = words[start : start + chunk_size]
        # The guard protects against adding an empty trailing window.
        if not chunk_words:
            break
        chunks.append(
            DocumentChunk(
                source=document.source,
                chunk_number=chunk_number,
                text=" ".join(chunk_words),
            )
        )
    return chunks


def chunk_documents(
    documents: list[Document], chunk_size: int = 120, overlap: int = 20
) -> list[DocumentChunk]:
    """Chunk every document while preserving source and chunk metadata.

    Each document is delegated to ``chunk_document`` so validation and window
    behavior stay in one place.
    """
    chunks: list[DocumentChunk] = []
    # Extend rather than append so callers receive one flat searchable list.
    for document in documents:
        chunks.extend(chunk_document(document, chunk_size, overlap))
    return chunks