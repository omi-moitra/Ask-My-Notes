"""Tests for literal keyword ranking.

Contents:
        - ``test_keyword_search_ranks_matching_terms_and_limits_results`` checks
            ranking and result limits.
        - ``test_keyword_search_handles_empty_queries`` checks empty input.
        - ``test_tokenize_filters_exact_words_and_preserves_meaningful_tokens``
            checks the fixed vocabulary and retained token content.
        - ``test_stop_words_do_not_create_matches_or_change_query_scores``
            checks the comparison fixture and equivalent queries.
        - ``test_search_handles_empty_tokens_and_nonpositive_limits`` checks
            empty query/corpus behavior and safe handling of empty chunks.
        - ``test_retained_length_ties_limits_and_original_metadata`` checks
            normalization, deterministic ordering, and preserved passages.
"""

from src.models import DocumentChunk
from src.search import STOP_WORDS, KeywordRetriever, tokenize


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


def test_tokenize_filters_exact_words_and_preserves_meaningful_tokens():
    """Exclude the specified vocabulary without damaging other token content."""
    # Use a literal expected vocabulary so accidental additions/removals fail.
    vocabulary = "a an and are as at be by does for from how in is it of on or that the this to was were what with"
    assert STOP_WORDS == frozenset(vocabulary.split())
    assert isinstance(STOP_WORDS, frozenset)
    assert tokenize(vocabulary.upper()) == []
    assert tokenize("THE theory is useful") == ["theory", "useful"]
    # Negation, numbers, ordering, and repetition must survive normalization.
    assert tokenize("not never no python python 123") == [
        "not", "never", "no", "python", "python", "123",
    ]


def test_stop_words_do_not_create_matches_or_change_query_scores():
    """Remove the controlled false match while preserving relevant passages."""
    chunks = [
        DocumentChunk("filler.txt", 1, "how is how is how is"),
        DocumentChunk("retrieval.md", 1, "retrieval finds useful passages"),
    ]
    retriever = KeywordRetriever(chunks)
    results = retriever.search("how is retrieval")
    # Equality includes scores and full original metadata, not just filenames.
    assert results == retriever.search("retrieval")
    assert results == retriever.search("retrieval retrieval")
    assert [result.chunk for result in results] == [chunks[1]]
    assert retriever.search("the is how") == []


def test_search_handles_empty_tokens_and_nonpositive_limits():
    """Empty token sets are valid for queries, individual chunks, or a corpus."""
    filler = DocumentChunk("filler.txt", 1, "the is how")
    useful = DocumentChunk("notes.txt", 1, "retrieval")
    # Exercise both empty retained-token counts and a truly empty collection.
    for chunks in ([], [filler], [filler, useful]):
        retriever = KeywordRetriever(chunks)
        for query in ("", "   ", "?!...", "the is how", "unmatched"):
            assert retriever.search(query) == []
        for limit in (0, -1):
            assert retriever.search("retrieval", limit=limit) == []
    assert KeywordRetriever([filler]).search("retrieval") == []
    assert KeywordRetriever([]).search("retrieval") == []


def test_retained_length_ties_limits_and_original_metadata():
    """Extra stop words do not penalize scores or alter displayed passages."""
    # Reverse source/chunk order and vary excluded words to expose both sorts
    # of regressions: normalization by raw length and unstable tie-breaking.
    chunks = [
        DocumentChunk("z.txt", 1, "retrieval useful"),
        DocumentChunk("a.md", 2, "the retrieval is useful"),
        DocumentChunk("a.md", 1, "how retrieval useful is"),
    ]
    retriever = KeywordRetriever(chunks)
    results = retriever.search("retrieval")
    assert [result.chunk for result in results] == [chunks[2], chunks[1], chunks[0]]
    assert len({result.score for result in results}) == 1
    assert retriever.search("retrieval", limit=2) == results[:2]
