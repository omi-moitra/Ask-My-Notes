"""Controlled local-adapter checks without a server or model download.

Contents:
    - Fake HTTP objects exercise the actual transport and request payloads.
    - Preflight cases reject missing, changed, remote, or incompatible assets.
    - Transport cases protect loopback-only, bounded, nonretrying behavior.
"""

import json
from types import SimpleNamespace

import pytest

from src.answering import AnswerError, SYSTEM_PROMPT, build_context
from src.local_generator import DEFAULT_MODEL, MODEL_DIGEST, LocalGenerator
from src.models import DocumentChunk, SearchResult


def context(text="Retrieval finds passages."):
    """Make a realistic bounded context without encoding or loading notes."""
    return build_context([SearchResult(DocumentChunk("note.md", 1, text), 1)])


def install_transport(monkeypatch, responses):
    """Replace only the socket boundary, retaining actual HTTP request logic."""
    calls = []
    class Connection:
        """Capture all connection/request settings and supply queued responses."""
        sock = None
        def __init__(self, host, port, timeout):
            self.record = dict(host=host, port=port, timeout=timeout)
            calls.append(self.record)
        def request(self, method, path, body, headers):
            self.record.update(method=method, path=path, body=json.loads(body) if body else None)
        def getresponse(self):
            value = responses.pop(0)
            if isinstance(value, Exception):
                raise value
            status, payload = value if isinstance(value, tuple) else (200, value)
            data = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
            chunks = [data, b""]
            return SimpleNamespace(status=status, fp=None, read1=lambda count: chunks.pop(0))
        def close(self):
            self.record["closed"] = True
    monkeypatch.setattr("src.local_generator.http.client.HTTPConnection", Connection)
    return calls


def model_tags(**changes):
    """Return the trusted local manifest fields, allowing one deliberate defect."""
    model = {"name": DEFAULT_MODEL, "digest": MODEL_DIGEST,
             "details": {"format": "gguf", "family": "qwen2"}}
    model.update(changes)
    return {"models": [model]}


def complete(**changes):
    """A completed runtime envelope still requires shared answer validation."""
    data = {"done": True, "done_reason": "stop", "message": {
        "content": '{"status":"insufficient_evidence","claims":[]}'}, "eval_count": 12}
    data.update(changes)
    return data


def test_fixed_loopback_schema_no_proxy_redirect_pull_or_retry(monkeypatch):
    """Host/proxy environment cannot route note content to another endpoint."""
    monkeypatch.setenv("HTTP_PROXY", "http://secret.example:80")
    monkeypatch.setenv("OLLAMA_HOST", "https://external.example")
    calls = install_transport(monkeypatch, [model_tags(), {}, {"version": "test"}, complete()])
    generator = LocalGenerator()
    assert "insufficient_evidence" in generator.generate("question", context())
    assert [c["path"] for c in calls] == ["/api/tags", "/api/show", "/api/version", "/api/chat"]
    assert all(c["host"] == "127.0.0.1" and c["port"] == 11434 and c["closed"] for c in calls)
    payload = calls[-1]["body"]
    assert payload["stream"] is False and payload["keep_alive"] == 0
    assert payload["options"]["num_predict"] == 512
    assert payload["messages"][0]["content"] == SYSTEM_PROMPT
    assert json.loads(payload["messages"][1]["content"])["question"] == "question"
    assert payload["format"]["properties"]["claims"]["items"]["properties"]["citations"]["items"]["enum"] == ["S1"]
    assert generator.metadata["digest"] == MODEL_DIGEST


@pytest.mark.parametrize("value", ["qwen2.5:1.5b-cloud", "https://external/model", "other", ""])
def test_unapproved_model_rejected_before_network(monkeypatch, value):
    """No cloud alias, URL, or accidental empty config can reach the transport."""
    monkeypatch.setenv("ASK_NOTES_LOCAL_MODEL", value)
    calls = install_transport(monkeypatch, [])
    with pytest.raises(AnswerError, match="supports only local"):
        LocalGenerator()
    assert not calls


@pytest.mark.parametrize("tags", [
    {"models": []}, {"models": "bad"}, model_tags(digest="different"),
    model_tags(details={"format": "cloud", "family": "qwen2"}),
])
def test_bad_model_preflight_never_submits_question(monkeypatch, tags):
    """Missing or changed assets produce guidance without automatic downloads."""
    calls = install_transport(monkeypatch, [tags])
    with pytest.raises(AnswerError):
        LocalGenerator().generate("private question", context())
    assert len(calls) == 1
    assert calls[0]["body"] is None


def test_remote_model_metadata_is_rejected(monkeypatch):
    """Even a local tag must not resolve to a cloud-backed model."""
    calls = install_transport(monkeypatch, [model_tags(), {"remote_host": "cloud.example"}])
    with pytest.raises(AnswerError, match="Cloud-backed"):
        LocalGenerator().generate("question", context())
    assert len(calls) == 2


@pytest.mark.parametrize("failure", [
    (302, {"location": "https://external"}), (500, {"error": "private note"}),
    (404, {}), b"bad JSON", b"x" * 1_000_001, TimeoutError("private"), OSError("private"),
])
def test_transport_failures_are_bounded_redacted_and_not_retried(monkeypatch, failure):
    """No response body or exception snippet escapes into user diagnostics."""
    calls = install_transport(monkeypatch, [failure])
    with pytest.raises(AnswerError) as exc:
        LocalGenerator().generate("question", context())
    assert "private" not in str(exc.value)
    assert len(calls) == 1 and calls[0]["closed"]


@pytest.mark.parametrize("envelope", [
    complete(done=False), complete(done_reason="length"), complete(message={"content": "x" * 8001}),
    complete(message={"content": "{}", "tool_calls": [{}]}), complete(message="wrong"),
])
def test_incomplete_or_unsupported_output_never_becomes_an_answer(monkeypatch, envelope):
    """Do not show truncated output or execute generated tool calls."""
    calls = install_transport(monkeypatch, [model_tags(), {}, {"version": "test"}, envelope])
    with pytest.raises(AnswerError):
        LocalGenerator().generate("question", context())
    assert len(calls) == 4


def test_conservative_token_bound_and_invalid_timeout_prevent_requests(monkeypatch):
    """Multibyte inputs can exhaust token capacity before the character budget."""
    calls = install_transport(monkeypatch, [])
    with pytest.raises(AnswerError, match="context bound"):
        LocalGenerator().generate("question", context("中" * 7000))
    for timeout in [0, -1, float("nan"), float("inf"), 121]:
        with pytest.raises(ValueError):
            LocalGenerator(timeout=timeout)
    assert not calls
