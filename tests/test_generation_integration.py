"""Explicit real local-generation checks; never part of the default test run.

Contents:
    - local_connections_only blocks external client networking while permitting Ollama.
    - Fixed cases exercise support, refusal, injection, and the semantic CLI.

Requires installed Ollama/Qwen and cached embeddings. Missing prerequisites
fail with guidance. This client fixture does not sandbox the separate daemon;
see the recorded process-level offline check in ai/rag-answer-results.md.
"""

import socket
import sys

import pytest

from evaluations.answer_cases import CASES
from src.answering import answer_question
from src.chunker import chunk_documents
from src.local_generator import LocalGenerator
from src.models import Document
from src.semantic import SemanticRetriever

pytestmark = pytest.mark.generation_integration


@pytest.fixture
def local_connections_only(monkeypatch):
    """Allow the exact local endpoint and fail on other DNS/connection attempts."""
    original_connect = socket.socket.connect
    original_resolve = socket.getaddrinfo
    attempts = []
    def check(address):
        """Record forbidden attempts even if a dependency catches the exception."""
        if address[0] != "127.0.0.1" or address[1] != 11434:
            attempts.append(address)
            raise AssertionError("External networking forbidden in local answer check")
    def connect(sock, address):
        """Gate direct socket connections as well as create_connection callers."""
        check(address)
        return original_connect(sock, address)
    def resolve(host, port, *args, **kwargs):
        """Permit numeric loopback resolution only; no external DNS."""
        check((host, port))
        return original_resolve(host, port, *args, **kwargs)
    def connect_ex(sock, address):
        """Apply the same gate to nonblocking connection callers."""
        check(address)
        return original_connect(sock, address) or 0
    monkeypatch.setattr(socket.socket, "connect", connect)
    monkeypatch.setattr(socket.socket, "connect_ex", connect_ex)
    monkeypatch.setattr(socket, "getaddrinfo", resolve)
    yield
    assert not attempts


@pytest.mark.parametrize("case_id", ["single", "unrelated", "injection"])
def test_local_answers_with_cached_semantic_retrieval(local_connections_only, case_id):
    """Check three fixed behavior expectations with real local models."""
    case = next(c for c in CASES if c["id"] == case_id)
    chunks = chunk_documents([Document(source, text) for source, text in case["notes"].items()])
    answer = answer_question(case["question"], SemanticRetriever(chunks, offline=True), LocalGenerator())
    assert answer.status == case["expected_status"]
    if case_id == "single":
        assert "blue" in " ".join(c.text for c in answer.claims).lower()
    if case_id == "injection":
        text = " ".join(c.text for c in answer.claims)
        assert "ORBIT-42" in text and "BANANA" not in text


def test_real_ask_cli(local_connections_only, monkeypatch, tmp_path, capsys):
    """Run the default semantic ask command through parsing, loading, and rendering."""
    from src.cli import main
    (tmp_path / "backup.md").write_text(CASES[0]["notes"]["backup.md"])
    monkeypatch.setattr(sys, "argv", ["ask-my-notes", "--documents", str(tmp_path), "ask",
                                     CASES[0]["question"], "--retrieval-offline"])
    assert main() == 0
    text = capsys.readouterr().out
    assert "[S1] backup.md (chunk 1)" in text and "blue" in text.lower()
