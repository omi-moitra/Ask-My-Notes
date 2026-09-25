"""CLI integration without model downloads.

Contents:
    - ``invoke`` drives real argument parsing against temporary notes.
    - Selection and option tests protect keyword compatibility and semantic/hybrid wiring.
    - Hybrid verbose tests inspect branch diagnostics using a fake encoder.
    - Failure tests check actionable messages and intentional exit statuses.
"""

import sys
from types import SimpleNamespace

import pytest

from src import cli
from src.models import SearchResult
from src.semantic import SemanticError


def invoke(monkeypatch, tmp_path, *options):
    """Supply one real note; use public main so loading and formatting run too."""
    (tmp_path / "note.md").write_text("retrieval finds useful passages")
    monkeypatch.setattr(sys, "argv", ["ask", "--documents", str(tmp_path), "search", "retrieval", *options])
    return cli.main()


@pytest.mark.parametrize("options", [(), ("--retriever", "keyword")])
def test_keyword_needs_no_semantic_dependencies(monkeypatch, tmp_path, capsys, options):
    """Keyword default and explicit selection both survive blocked ML imports."""
    monkeypatch.setitem(sys.modules, "sentence_transformers", None)
    assert invoke(monkeypatch, tmp_path, *options) == 0
    assert "note.md (chunk 1)" in capsys.readouterr().out


@pytest.mark.parametrize("options", [("--offline",), ("--model-cache", "somewhere"),
                                       ("--retriever", "unknown")])
def test_invalid_options_are_usage_errors(monkeypatch, tmp_path, options):
    """Reject meaningless options before collection/model work."""
    with pytest.raises(SystemExit) as exc:
        invoke(monkeypatch, tmp_path, *options)
    assert exc.value.code == 2


@pytest.mark.parametrize("mode", ["semantic", "hybrid"])
def test_semantic_selection_preserves_result_format(monkeypatch, tmp_path, capsys, mode):
    """Exercise real CLI parsing while recording semantic constructor settings."""
    calls = []

    def retriever(chunks, **kwargs):
        """Return the existing shared result object, as the real retriever does."""
        calls.append(kwargs)
        return SimpleNamespace(search=lambda query, limit: [SearchResult(chunks[0], 0.75)])

    monkeypatch.setattr(cli, "HybridRetriever" if mode == "hybrid" else "SemanticRetriever", retriever)
    assert invoke(monkeypatch, tmp_path, "--retriever", mode, "--offline",
                  "--model-cache", str(tmp_path)) == 0
    assert calls == [dict(cache=tmp_path, offline=True)]
    assert "1. [0.750] note.md (chunk 1)" in capsys.readouterr().out


@pytest.mark.parametrize("mode", ["semantic", "hybrid"])
def test_model_failure_is_exit_one_without_fallback(monkeypatch, tmp_path, caplog, capsys, mode):
    """A model failure must not be mistaken for a successful keyword search."""
    def fail(query, limit):
        """Use the domain exception the CLI is allowed to translate."""
        raise SemanticError("Populate this same cache with an online semantic search first.")

    monkeypatch.setattr(cli, "HybridRetriever" if mode == "hybrid" else "SemanticRetriever", lambda *a, **kw: SimpleNamespace(search=fail))
    assert invoke(monkeypatch, tmp_path, "--retriever", mode) == 1
    assert "Populate this same cache" in caplog.text
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize("mode", ["semantic", "hybrid"])
def test_missing_dependency_and_blank_query(monkeypatch, tmp_path, caplog, capsys, mode):
    """Missing packages fail for real work, but an empty request needs no model."""
    monkeypatch.setitem(sys.modules, "sentence_transformers", None)
    assert invoke(monkeypatch, tmp_path, "--retriever", mode) == 1
    assert "pip install" in caplog.text
    assert invoke(monkeypatch, tmp_path, "--retriever", mode, "--limit", "0") == 0
    assert "No matching passages found." in capsys.readouterr().out


def test_hybrid_verbose_reports_policy_and_counts(monkeypatch, tmp_path, caplog, capsys):
    """Exercise real fusion while making only the model adapter deterministic."""
    import logging
    from src.semantic import SentenceTransformerEncoder

    monkeypatch.setattr(SentenceTransformerEncoder, "encode", lambda self, texts: [[1, 0] for _ in texts])
    with caplog.at_level(logging.DEBUG):
        assert invoke(monkeypatch, tmp_path, "--retriever", "hybrid") == 0
    assert "Retriever: hybrid" in caplog.text
    assert "constant=60 eligible_chunks=1 keyword_results=1 semantic_results=1" in caplog.text
    assert "revision=" in caplog.text and "cache=" in caplog.text
    stdout = capsys.readouterr().out
    assert "[0.033] note.md (chunk 1)" in stdout
    assert "constant=" not in stdout
