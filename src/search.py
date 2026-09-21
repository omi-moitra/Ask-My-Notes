"""A small, explainable keyword retriever.

Contents:
    - ``tokenize`` for the shared query and passage token rules.
    - ``KeywordRetriever`` for indexing chunks and ranking searches.
"""

import math
import re
from collections import Counter

from .models import DocumentChunk, Retriever, SearchResult

TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    """Return lowercase alphanumeric terms.

    Literal matching is intentional for this milestone: stemming and synonym
    expansion belong in a later semantic or hybrid retrieval layer.
    """
    # Lowercasing makes capitalization irrelevant to matching.
    return TOKEN_PATTERN.findall(text.lower())


class KeywordRetriever(Retriever):
    """Rank chunks with a compact TF-IDF-inspired keyword score.

    Initialization precomputes term counts and inverse document frequency so
    each query only performs the work needed for its matching terms.
    """

    def __init__(self, chunks: list[DocumentChunk]) -> None:
        """Build the small in-memory index used by ``search``."""
        self.chunks = chunks
        # Count terms once per chunk so query handling remains easy to read.
        self.term_counts = [Counter(tokenize(chunk.text)) for chunk in chunks]
        # A term's document frequency counts chunks, not repeated occurrences.
        document_frequency = Counter(
            term for counts in self.term_counts for term in counts.keys()
        )
        # Rare terms receive more weight; smoothing avoids division by zero.
        self.inverse_document_frequency = {
            term: math.log((1 + len(chunks)) / (1 + frequency)) + 1
            for term, frequency in document_frequency.items()
        }

    def search(self, query: str, limit: int = 3) -> list[SearchResult]:
        """Return the highest-scoring chunks for a query.

        Queries are tokenized, non-matching chunks are skipped, and matching
        chunks are sorted deterministically before the requested limit applies.
        """
        # A non-positive limit is a valid request for no output.
        if limit <= 0:
            return []
        # Set semantics prevent repeating a query word from inflating its score.
        query_terms = set(tokenize(query))
        if not query_terms:
            return []

        results: list[SearchResult] = []
        # Zip keeps each chunk paired with the counts computed at initialization.
        for chunk, counts in zip(self.chunks, self.term_counts):
            matched_terms = query_terms & counts.keys()
            # A chunk with no shared terms cannot contribute to keyword search.
            if not matched_terms:
                continue
            # Cap repetition, apply rarity weighting, and normalize for length.
            score = sum(
                min(counts[term], 3) * self.inverse_document_frequency.get(term, 1.0)
                for term in matched_terms
            ) / math.sqrt(sum(counts.values()))
            results.append(SearchResult(chunk=chunk, score=score))

        # Tie-breakers make repeated runs stable and useful for tests and users.
        return sorted(
            results,
            key=lambda result: (
                -result.score,
                result.chunk.source,
                result.chunk.chunk_number,
            ),
        )[:limit]