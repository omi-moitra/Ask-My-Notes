"""Explicit real-model acceptance checks with network connections prohibited.

Contents:
    - ``block_network`` fails on any attempted socket connection or DNS lookup.
    - ``test_real_model_comparison`` compares all three modes without relabeling.
    - ``test_empty_offline_cache`` verifies prompt setup failure without fallback.
    - ``test_offline_cli_success_and_missing_cache`` checks real CLI output/status.

Run with: .venv-semantic/bin/python -m pytest -m integration -s
First populate the default cache through an online semantic CLI search.
Missing prerequisites fail rather than silently skipping these explicit checks.
"""

import importlib.metadata
import json
import platform
import socket

import pytest

from src.hybrid import HybridRetriever, RRF_CONSTANT
from src.chunker import chunk_documents
from src.search import KeywordRetriever, tokenize
from src.semantic import MODEL_ID, MODEL_REVISION, SemanticError, SemanticRetriever
from fixtures.semantic_cases import DOCUMENTS, QUERIES

pytestmark = pytest.mark.integration


@pytest.fixture
def block_network(monkeypatch):
    """Fail even when dependencies attempt networking and swallow its error."""
    attempts = []

    def deny(*args, **kwargs):
        """Record and prohibit transport/DNS calls; no actual connection occurs."""
        attempts.append(True)
        raise AssertionError("Network use is forbidden in offline integration checks")

    monkeypatch.setattr(socket.socket, "connect", deny)
    monkeypatch.setattr(socket.socket, "connect_ex", deny)
    monkeypatch.setattr(socket, "create_connection", deny)
    monkeypatch.setattr(socket, "getaddrinfo", deny)
    yield
    assert not attempts, "Offline loading attempted network access"


def test_real_model_comparison(block_network):
    """Verify predetermined labels using identical chunks for both retrievers."""
    chunks = chunk_documents(DOCUMENTS, chunk_size=120, overlap=20)
    keyword = KeywordRetriever(chunks)
    hybrid = HybridRetriever(chunks, offline=True)
    semantic = hybrid.semantic
    report = {"model": MODEL_ID, "revision": MODEL_REVISION,
              "python": platform.python_version(), "platform": platform.platform(),
              "chunk_size": 120, "overlap": 20, "rrf_constant": RRF_CONSTANT, "results": []}
    recovered = 0
    for kind, query, expected in QUERIES:
        lexical = keyword.search(query)
        dense = semantic.search(query)
        combined = hybrid.search(query, limit=len(chunks))
        assert len({(r.chunk.source, r.chunk.chunk_number) for r in combined}) == len(chunks)
        assert hybrid.search(query, limit=1) == combined[:1]
        report["results"].append({"kind": kind, "query": query, "expected": expected,
            "keyword": [(r.chunk.source, r.score) for r in lexical],
            "semantic": [(r.chunk.source, r.score) for r in dense],
            "hybrid": [(r.chunk.source, r.score) for r in combined[:3]],
            "hybrid_answer_rank": next((i for i, r in enumerate(combined, 1)
                                         if r.chunk.source == expected), None)})
        if kind == "exact":
            assert lexical[0].chunk.source == expected
            assert dense[0].chunk.source == expected
        elif kind == "paraphrase":
            passage = next(c.text for c in chunks if c.source == expected)
            assert not (set(tokenize(query)) & set(tokenize(passage)))
            assert expected in [r.chunk.source for r in dense]
            recovered += expected not in [r.chunk.source for r in lexical]
        else:
            # No threshold exists: unrelated questions still receive neighbors.
            assert len(dense) == 3
    assert recovered >= 1
    report["packages"] = {name: importlib.metadata.version(name) for name in (
        "sentence-transformers", "torch", "transformers", "huggingface-hub", "numpy",
        "tokenizers", "scikit-learn", "scipy",
    )}
    print("\nHYBRID_COMPARISON=" + json.dumps(report, sort_keys=True))


@pytest.mark.parametrize("retriever_type", [SemanticRetriever, HybridRetriever])
def test_empty_offline_cache(block_network, tmp_path, retriever_type):
    """An absent cached revision must fail with instructions, without networking."""
    with pytest.raises(SemanticError, match="Populate this same cache"):
        retriever_type(chunk_documents(DOCUMENTS), cache=tmp_path, offline=True).search("files")


@pytest.mark.parametrize("mode", ["semantic", "hybrid"])
def test_offline_cli_success_and_missing_cache(block_network, monkeypatch, tmp_path, capsys, caplog, mode):
    """Exercise actual CLI output and exit codes with both populated and empty caches."""
    import sys
    from src.cli import main

    notes = tmp_path / "notes"
    notes.mkdir()
    (notes / "backup.md").write_text(DOCUMENTS[0].text)
    args = ["ask", "--documents", str(notes), "search", "recover deleted files",
            "--retriever", mode, "--offline"]
    monkeypatch.setattr(sys, "argv", args)
    assert main() == 0
    assert "backup.md (chunk 1)" in capsys.readouterr().out
    monkeypatch.setattr(sys, "argv", args + ["--model-cache", str(tmp_path / "empty-cache")])
    assert main() == 1
    assert capsys.readouterr().out == ""
    assert "Populate this same cache" in caplog.text
