"""Tests for literal keyword ranking.

Contents:
        - ``test_keyword_search_ranks_matching_terms_and_limits_results`` checks
            ranking and result limits.
        - ``test_keyword_search_handles_empty_queries`` checks empty input.
"""

from src.models import DocumentChunk
from src.search import KeywordRetriever


def test_keyword_search_ranks_matching_terms_and_limits_results():
    """Rank the more relevant passage and respect the requested limit."""
    # Include two matching passages and one unrelated passage for comparison.
    chunks = [
        DocumentChunk("python.txt", 1, "Python functions have clear responsibilities."),
        DocumentChunk("retrieval.md", 1, "Retrieval finds useful passages from documents."),
        DocumentChunk("other.txt", 1, "Documents search uses keywords."),
    ]

    # Retrieval matches multiple literal terms and should outrank one-term text.
    results = KeywordRetriever(chunks).search("how does retrieval find documents?", limit=2)

    # Only the two relevant chunks should remain, in score order.
    assert len(results) == 2
    assert results[0].chunk.source == "retrieval.md"
    assert results[0].score > results[1].score


def test_keyword_search_handles_empty_queries():
    """Return no results when tokenization produces no query terms."""
    assert KeywordRetriever([]).search("   ") == []