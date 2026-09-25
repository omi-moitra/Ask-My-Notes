"""Exercise the public ask CLI without running an embedding or answer model.

Contents:
    - invoke supplies temporary notes and real argument parsing.
    - Success tests verify defaults, rendering, and empty evidence.
    - Failure tests cover input/setup errors without partial output or networking.
"""

import sys
from types import SimpleNamespace

import pytest

from src import cli
from src.answering import ABSTENTION, AnswerError
from src.models import SearchResult


def invoke(monkeypatch, tmp_path, *args, query="retrieval"):
    """Use the actual loader and chunker against one minimal temporary note."""
    (tmp_path / "note.md").write_text("Retrieval finds useful passages.")
    monkeypatch.setattr(sys, "argv", ["ask-my-notes", "--documents", str(tmp_path), "ask", query, *args])
    return cli.main()


@pytest.mark.parametrize("mode", ["semantic", "hybrid", "keyword"])
def test_ask_wires_retriever_and_formats_original_evidence(monkeypatch, tmp_path, capsys, mode):
    """Default semantic and explicit alternatives share the answer renderer."""
    configs, requests = [], []
    def retriever(chunks, **kwargs):
        """Capture cache/offline settings while retaining original chunk records."""
        configs.append(kwargs)
        return SimpleNamespace(search=lambda query, limit: [SearchResult(chunks[0], 0.5)])
    generator = SimpleNamespace(generate=lambda q, c: requests.append((q, c)) or
        '{"status":"answered","claims":[{"text":"Retrieval finds useful passages.","citations":["S1"]}]}')
    monkeypatch.setattr(cli, "LocalGenerator", lambda: generator)
    options = [] if mode == "semantic" else ["--retriever", mode]
    if mode != "keyword":
        monkeypatch.setattr(cli, "SemanticRetriever" if mode == "semantic" else "HybridRetriever", retriever)
        options += ["--retrieval-offline", "--model-cache", str(tmp_path)]
    assert invoke(monkeypatch, tmp_path, *options) == 0
    assert len(requests) == 1
    assert "[S1] note.md (chunk 1)" in capsys.readouterr().out
    if mode != "keyword":
        assert configs == [{"cache": tmp_path, "offline": True}]


@pytest.mark.parametrize("args,query", [
    (("--limit", "0"), "question"), (("--limit", "21"), "question"),
    (("--context-chars", "1"), "question"), (("--context-chars", "12001"), "question"),
    (("--offline",), "question"), (("--retriever", "keyword", "--retrieval-offline"), "question"),
    (("--retriever", "keyword", "--model-cache", "cache"), "question"),
    ((), " "), ((), "x" * 2001),
])
def test_bad_ask_options_fail_before_model_work(monkeypatch, tmp_path, args, query):
    """Usage errors must not start expensive components or contact the daemon."""
    monkeypatch.setattr(cli, "LocalGenerator", lambda: pytest.fail("unexpected construction"))
    with pytest.raises(SystemExit) as exc:
        invoke(monkeypatch, tmp_path, *args, query=query)
    assert exc.value.code == 2


def test_empty_evidence_does_not_generate(monkeypatch, tmp_path, capsys):
    """Keyword search with no shared terms returns a successful abstention."""
    monkeypatch.setattr(cli, "LocalGenerator", lambda: SimpleNamespace(
        generate=lambda *args: pytest.fail("unexpected generation")))
    assert invoke(monkeypatch, tmp_path, "--retriever", "keyword", query="zebra") == 0
    assert capsys.readouterr().out.strip() == ABSTENTION


def test_generation_failure_and_malformed_answer_are_operational_errors(monkeypatch, tmp_path, capsys, caplog):
    """No success output is produced for an unavailable or malformed model."""
    def fail(*args):
        """Simulate the stable error boundary exposed by the local adapter."""
        raise AnswerError("Local runtime unavailable")
    for generate in [fail, lambda *args: "bad JSON"]:
        monkeypatch.setattr(cli, "LocalGenerator", lambda: SimpleNamespace(generate=generate))
        assert invoke(monkeypatch, tmp_path, "--retriever", "keyword") == 1
        assert capsys.readouterr().out == ""
    assert "Local runtime unavailable" in caplog.text


def test_missing_notes_and_invalid_chunk_settings(monkeypatch, tmp_path, capsys):
    """Ask adds actionable errors without changing existing search semantics."""
    monkeypatch.setattr(sys, "argv", ["ask", "--documents", str(tmp_path / "missing"), "ask", "q"])
    assert cli.main() == 1
    assert not capsys.readouterr().out
    monkeypatch.setattr(sys, "argv", ["ask", "--chunk-size", "0", "ask", "q"])
    with pytest.raises(SystemExit) as exc:
        cli.main()
    assert exc.value.code == 2
