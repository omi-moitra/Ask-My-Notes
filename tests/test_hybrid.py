"""Model-free verification of reciprocal-rank fusion and branch composition.

Contents:
    - ``result`` and ``FakeEncoder`` build transparent ranking/vector fixtures.
    - Fusion tests cover ranks, identity rules, limits, ties, and regressions.
    - Retriever tests cover full candidate depth, snapshots, reuse, and failures.
"""

import logging
from types import SimpleNamespace

import pytest

from src.hybrid import HybridRetriever, RRF_CONSTANT, fuse_rankings
from src.models import DocumentChunk, SearchResult
from src.semantic import SemanticError


def result(source, score=1.0, number=1, text=None):
    """Make identity explicit while allowing raw scores unrelated to list order."""
    return SearchResult(DocumentChunk(source, number, source if text is None else text), score)


class FakeEncoder:
    """Return exact vectors and record batches to reveal passage-index reuse."""

    def __init__(self, vectors):
        """Keep the mapping and call history separate from retriever state."""
        self.vectors = vectors
        self.calls = []

    def encode(self, texts):
        """Observe original sentences before returning their prepared vectors."""
        self.calls.append(list(texts))
        return [self.vectors[text] for text in texts]


def test_worked_example_uses_order_not_scores():
    """The spec's A/C/B order must survive arbitrary branch score magnitudes."""
    assert RRF_CONSTANT == 60
    output = fuse_rankings([result("A", 999), result("B", -4)],
                           [result("C", 0), result("A", -0.9)])
    assert [r.chunk.source for r in output] == ["A", "C", "B"]
    assert [r.score for r in output] == pytest.approx([
        0.03252247488101534, 0.01639344262295082, 0.016129032258064516,
    ])
    assert output == fuse_rankings([result("A", -100), result("B", 800)],
                                  [result("C", 90), result("A", 90)])


@pytest.mark.parametrize("empty_first", [False, True])
def test_one_empty_branch_preserves_order_with_new_scores(empty_first):
    """A single contributing branch is normal fusion, not a model-error fallback."""
    branch = [result("z", -0.1), result("a", -0.9)]
    output = fuse_rankings([] if empty_first else branch, branch if empty_first else [])
    assert [r.chunk for r in output] == [r.chunk for r in branch]
    assert [r.score for r in output] == pytest.approx([1 / 61, 1 / 62])
    assert fuse_rankings([], []) == []


def test_duplicate_positions_identity_and_original_text():
    """Duplicates vote once at their first position; same text is not identity."""
    a, b = result("a", text="same"), result("b", text="same")
    output = fuse_rankings([a, a, b], [b, a], 10)
    assert [r.chunk for r in output] == [a.chunk, b.chunk]
    # B's keyword contribution uses its actual third position, not a renumbered 2.
    assert output[1].score == pytest.approx(1 / 63 + 1 / 61)
    assert len(output) == 2


@pytest.mark.parametrize("across_branches", [False, True])
def test_conflicting_branch_text_is_rejected(across_branches):
    """Do not silently attach a fused score to one of two conflicting passages."""
    a, conflict = result("a", text="first"), result("a", text="different")
    with pytest.raises(ValueError, match="Conflicting text"):
        fuse_rankings([a] if across_branches else [a, conflict], [conflict] if across_branches else [])


def test_exact_ties_source_and_chunk_order_and_full_precision():
    """Symmetric ranks tie; source and chunk number make the result stable."""
    a1, a2, z = result("a", number=1), result("a", number=2), result("z")
    tied = fuse_rankings([z, a2, a1], [a1, a2, z], 10)
    # A1 and Z have ranks (3,1) and (1,3); their equal scores use source order.
    assert tied[0].score == tied[1].score
    assert [r.chunk for r in tied[:2]] == [a1.chunk, z.chunk]
    assert [r.chunk for r in fuse_rankings([a2], [a1])] == [a1.chunk, a2.chunk]
    # Both display as 0.016, but raw scores override alphabetical source order.
    close = fuse_rankings([z, a1], [])
    assert f"{close[0].score:.3f}" == f"{close[1].score:.3f}"
    assert close[0].chunk == z.chunk


def test_fusion_can_promote_irrelevant_literal_match():
    """A correct fusion algorithm can hurt relevance; keep the label honest."""
    irrelevant, relevant = result("noise"), result("answer")
    semantic = [relevant, irrelevant]
    assert semantic[0].chunk == relevant.chunk
    assert fuse_rankings([irrelevant], semantic)[0].chunk == irrelevant.chunk


def test_below_output_cutoffs_can_win_and_prefix_is_consistent(monkeypatch):
    """Request full N lists: a rank-two agreement can beat rank-one single votes."""
    chunks = [result(name).chunk for name in ("A", "B", "C", "D")]
    retriever = HybridRetriever(chunks)
    calls = []

    def branch(name, order):
        """Respect requested depth, exposing the bug if final limit leaks inward."""
        def search(query, limit):
            """Record the branch limit as part of the observable contract."""
            calls.append((name, limit))
            return [result(letter) for letter in order[:limit]]
        return SimpleNamespace(search=search)

    retriever.keyword = branch("keyword", ["A", "B", "C", "D"])
    retriever.semantic = branch("semantic", ["D", "B", "C", "A"])
    top = retriever.search("q", 1)
    all_results = retriever.search("q", 20)
    assert top == all_results[:1]
    assert top[0].chunk.source == "B"
    assert calls == [("keyword", 4), ("semantic", 4)] * 2


def test_snapshot_deduplication_real_composition_and_reuse(caplog):
    """Both branches share eligible chunks, while caller mutations cannot shift them."""
    a, b = DocumentChunk("a", 7, "save a copy"), DocumentChunk("b", 2, "bread rises")
    chunks = [a, a, b, DocumentChunk("blank", 1, "\n")]
    encoder = FakeEncoder({a.text: [1, 0], b.text: [0, 1], "recover files": [1, 0],
                           "the is how": [0, 1], "?!": [0, 1]})
    retriever = HybridRetriever(chunks, encoder=encoder)
    chunks.clear()
    with caplog.at_level(logging.DEBUG):
        results = retriever.search("recover files")
    assert [r.chunk for r in results] == [a, b]
    assert [r.score for r in results] == pytest.approx([1 / 61, 1 / 62])
    assert retriever.search("the is how")[0].chunk == b
    assert retriever.search("?!")[0].chunk == b
    assert encoder.calls == [[a.text, b.text], ["recover files"], ["the is how"], ["?!"]]
    assert "constant=60 eligible_chunks=2 keyword_results=0 semantic_results=2" in caplog.text


def test_conflicting_input_fails_before_encoder_use():
    """Conflicting identities cannot enter either branch's index."""
    encoder = FakeEncoder({})
    with pytest.raises(ValueError, match="Conflicting text"):
        HybridRetriever([result("a", text="x").chunk, result("a", text="y").chunk], encoder)
    assert encoder.calls == []


@pytest.mark.parametrize("texts,query,limit", [([], "q", 3), ([" "], "q", 3),
    (["text"], " \n", 3), (["text"], "q", 0), (["text"], "q", -2)])
def test_early_returns_do_not_call_either_branch(texts, query, limit):
    """Empty work avoids branch searches entirely, not merely model construction."""
    retriever = HybridRetriever([DocumentChunk("a", 1, text) for text in texts])

    def forbidden(*args, **kwargs):
        """Any branch invocation would violate the short-circuit guarantee."""
        pytest.fail("branch called for empty request")

    retriever.keyword = retriever.semantic = SimpleNamespace(search=forbidden)
    assert retriever.search(query, limit) == []
    assert fuse_rankings([result("a")], [], limit=0) == []


def test_semantic_failure_does_not_return_keyword_hits():
    """A failed model is an error even if lexical evidence was already found."""
    class BrokenEncoder:
        """Represent an expected model failure at the existing encoder boundary."""
        def encode(self, texts):
            """Raise the same domain error translated by the CLI."""
            raise SemanticError("model failed")

    retriever = HybridRetriever([result("a", text="retrieval").chunk], BrokenEncoder())
    with pytest.raises(SemanticError, match="model failed"):
        retriever.search("retrieval")
