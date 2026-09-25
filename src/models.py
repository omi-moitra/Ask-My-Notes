"""Data types shared by the ingestion and retrieval components.

Contents:
    - ``Document``: metadata and text for one source file.
    - ``DocumentChunk``: one searchable window from a source file.
    - ``SearchResult``: a chunk paired with its relevance score.
    - ``Retriever``: the shared interface for keyword, semantic, and hybrid search.
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
    why one passage was ranked above another. Keyword scores, cosine similarity,
    and hybrid reciprocal-rank scores have different scales, not probabilities.
    """

    chunk: DocumentChunk
    score: float


class Retriever:
    """Small interface shared by keyword, local semantic, and hybrid retrieval.

    All implementations return original passages through the same shape.
    Their scores have different meanings and must not be compared directly.
    """

    def search(self, query: str, limit: int = 3) -> list[SearchResult]:
        """Return at most ``limit`` ranked results for ``query``.

        Concrete retrievers provide the algorithm; this base method only
        documents the shared shape. Empty queries and nonpositive limits return
        no results, but a semantic nearest neighbor need not be relevant.
        """
        raise NotImplementedError
