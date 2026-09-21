"""Data types shared by the ingestion and retrieval components.

Contents:
    - ``Document``: metadata and text for one source file.
    - ``DocumentChunk``: one searchable window from a source file.
    - ``SearchResult``: a chunk paired with its relevance score.
    - ``Retriever``: the interface for keyword and future semantic search.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Document:
    """A source file loaded from the document collection.

    ``source`` is kept relative to the documents directory so output remains
    portable, while ``text`` contains the complete decoded file contents.
    """

    source: str
    text: str


@dataclass(frozen=True)
class DocumentChunk:
    """A searchable section of a source document.

    ``chunk_number`` is one-based because it is displayed to a person and can
    later be used as a citation reference.
    """

    source: str
    chunk_number: int
    text: str


@dataclass(frozen=True)
class SearchResult:
    """A ranked chunk returned by a retriever.

    The score is deliberately kept alongside the chunk so callers can show
    why one passage was ranked above another.
    """

    chunk: DocumentChunk
    score: float


class Retriever:
    """Small interface that future semantic retrievers can implement.

    Keeping this interface narrow means a later embedding retriever can be
    substituted without changing the ingestion pipeline or CLI formatting.
    """

    def search(self, query: str, limit: int = 3) -> list[SearchResult]:
        """Return at most ``limit`` ranked results for ``query``.

        Concrete retrievers provide the algorithm; this base method only
        documents the contract shared by all retriever implementations.
        """
        raise NotImplementedError