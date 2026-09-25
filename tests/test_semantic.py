"""Deterministic semantic tests requiring neither model assets nor ML packages.

Contents:
    - ``FakeEncoder`` provides observable inputs and hand-checkable vectors.
    - Ranking/lifecycle tests cover cosine, metadata, reuse, and empty inputs.
    - Malformed-output tests exercise batch and numeric validation.
    - Adapter tests isolate cache arguments, truncation, and expected failures.
"""

import sys
from types import SimpleNamespace

import pytest

from src.models import DocumentChunk
from src.semantic import (
    MODEL_ID, MODEL_REVISION, SemanticError, SemanticRetriever, SentenceTransformerEncoder,
)


class FakeEncoder:
    """Map exact original text to known vectors and record batch boundaries."""

    def __init__(self, vectors):
        """Keep vector fixtures outside production code so arithmetic is explicit."""
        self.vectors = vectors
        self.calls = []

    def encode(self, texts):
        """Record the actual request before returning vectors in matching order."""
        self.calls.append(list(texts))
        return [self.vectors[text] for text in texts]


def test_cosine_metadata_ties_limits_and_reuse():
    """Magnitudes do not affect cosine; equal directions use source/chunk ties."""
    chunks = [DocumentChunk("z", 1, "The positive"), DocumentChunk("a", 2, "Is same"),
              DocumentChunk("a", 1, "Another"), DocumentChunk("b", 1, "Orthogonal"),
              DocumentChunk("c", 1, "Opposite")]
    encoder = FakeEncoder({"The positive": [20, 0], "Is same": [1, 0], "Another": [2, 0],
                           "Orthogonal": [0, 1], "Opposite": [-1, 0], "the is how": [3, 0],
                           "?!": [3, 0]})
    retriever = SemanticRetriever(chunks, encoder)
    # Caller edits must not change the association with embedded passages.
    expected = [chunks[2], chunks[1], chunks[0], chunks[3], chunks[4]]
    chunks.clear()
    result = retriever.search("the is how", limit=10)
    assert [r.chunk for r in result] == expected
    assert [r.score for r in result] == pytest.approx([1, 1, 1, 0, -1])
    assert retriever.search("?!", 2) == result[:2]
    # Passage encoding happens once, and original stop words/punctuation reach
    # the encoder intact. Queries remain separate batches on repeated searches.
    assert encoder.calls == [["The positive", "Is same", "Another", "Orthogonal", "Opposite"],
                             ["the is how"], ["?!"]]


@pytest.mark.parametrize("chunks,query,limit", [
    ([], "query", 3), (["   "], "query", 3), (["text"], "   ", 3),
    (["text"], "query", 0), (["text"], "query", -1),
])
def test_short_circuits_never_encode(chunks, query, limit):
    """An empty request should work even when model packages are unavailable."""
    encoder = FakeEncoder({})
    retriever = SemanticRetriever([DocumentChunk("a", 1, t) for t in chunks], encoder)
    assert retriever.search(query, limit) == []
    assert encoder.calls == []


def test_whitespace_chunks_are_skipped_and_large_vectors_are_safe():
    """Blank chunks are not encoded; finite large components must not overflow."""
    chunk = DocumentChunk("original.md", 9, "  sentence  ")
    encoder = FakeEncoder({chunk.text: [1e308, 1e308], "q": [1, 1]})
    result = SemanticRetriever([DocumentChunk("blank", 1, "\n"), chunk], encoder).search("q")
    assert result[0].chunk == chunk
    assert result[0].score == pytest.approx(1)


@pytest.mark.parametrize("output", [None, [], [[1, 0], [1, 0]], [[]], [[0, 0]],
                                       [[float("nan"), 1]], [[float("inf"), 0]], [["bad", 1]]])
def test_invalid_passage_vectors_fail(output):
    """Invalid vectors must not reach sorting or produce plausible-looking scores."""
    encoder = SimpleNamespace(encode=lambda texts: output)
    with pytest.raises(SemanticError, match="Invalid encoder output"):
        SemanticRetriever([DocumentChunk("a", 1, "text")], encoder).search("q")


def test_inconsistent_passage_and_query_dimensions_fail():
    """Validate dimensions across the passage batch and again for each query."""
    chunks = [DocumentChunk("a", 1, "one"), DocumentChunk("b", 1, "two")]
    encoder = FakeEncoder({"one": [1, 0], "two": [1], "q": [1]})
    with pytest.raises(SemanticError, match="dimensions"):
        SemanticRetriever(chunks, encoder).search("q")
    with pytest.raises(SemanticError, match="dimensions"):
        SemanticRetriever(chunks[:1], encoder).search("q")


def install_fake_model(monkeypatch, model):
    """Supply a fake optional module without importing any real model package."""
    calls = []

    def constructor(path, **kwargs):
        """Record options so tests can assert the cache/offline boundary."""
        calls.append((path, kwargs))
        return model

    monkeypatch.setitem(sys.modules, "sentence_transformers", SimpleNamespace(SentenceTransformer=constructor))
    return calls


@pytest.mark.parametrize("offline", [False, True])
def test_adapter_pinned_cache_loading_and_truncation(monkeypatch, tmp_path, caplog, offline):
    """Use a fake tokenizer to test warnings without long real-model inference."""
    encoded = []

    def encode(texts, **kwargs):
        """Record original inputs and required model encoding arguments."""
        encoded.append((texts, kwargs))
        return [[1, 0] for _ in texts]

    model = SimpleNamespace(max_seq_length=3, encode=encode,
                            tokenizer=lambda texts, **kwargs: {"input_ids": [list(range(len(t))) for t in texts]})
    calls = install_fake_model(monkeypatch, model)
    snapshots = []

    def snapshot(path, **kwargs):
        """An offline snapshot must be resolved from the same pinned cache."""
        snapshots.append((path, kwargs))
        return str(tmp_path / "snapshot")

    monkeypatch.setitem(sys.modules, "huggingface_hub", SimpleNamespace(snapshot_download=snapshot))
    adapter = SentenceTransformerEncoder(tmp_path, offline)
    assert calls == []  # Construction has no model side effects.
    adapter.encode(["long sentence"])
    adapter.encode(["q"])
    assert len(calls) == 1
    path, options = calls[0]
    assert path == (str(tmp_path / "snapshot") if offline else MODEL_ID)
    assert options == dict(revision=MODEL_REVISION, device="cpu", cache_folder=str(tmp_path),
                           local_files_only=offline, trust_remote_code=False)
    assert len(snapshots) == int(offline)
    if offline:
        assert snapshots[0][1] == dict(revision=MODEL_REVISION, cache_dir=str(tmp_path), local_files_only=True)
    assert "will be truncated" in caplog.text
    assert encoded[0] == (["long sentence"], dict(batch_size=32, normalize_embeddings=True,
                                                   show_progress_bar=False, convert_to_numpy=True))


def test_missing_dependency_has_install_guidance(monkeypatch):
    """Missing optional packages should not leak an import traceback to users."""
    monkeypatch.setitem(sys.modules, "sentence_transformers", None)
    with pytest.raises(SemanticError, match="pip install"):
        SentenceTransformerEncoder().encode(["text"])


@pytest.mark.parametrize("offline", [False, True])
def test_load_failure_has_actionable_guidance(monkeypatch, tmp_path, offline):
    """Download/cache errors are expected operational failures, not empty results."""
    def fail(*args, **kwargs):
        """Represent a failed download or missing cached snapshot."""
        raise OSError("unavailable")

    monkeypatch.setitem(sys.modules, "sentence_transformers", SimpleNamespace(SentenceTransformer=fail))
    monkeypatch.setitem(sys.modules, "huggingface_hub", SimpleNamespace(snapshot_download=fail))
    with pytest.raises(SemanticError, match="Populate this same cache" if offline else "network access"):
        SentenceTransformerEncoder(tmp_path, offline).encode(["text"])


def test_encoding_failure_is_reported(monkeypatch):
    """Known backend runtime failures become a concise semantic error."""
    def fail(*args, **kwargs):
        """Represent a backend allocation or inference failure."""
        raise RuntimeError("out of memory")

    adapter = SentenceTransformerEncoder()
    adapter._model = SimpleNamespace(tokenizer=fail)
    with pytest.raises(SemanticError, match="encoding failed"):
        adapter.encode(["text"])
