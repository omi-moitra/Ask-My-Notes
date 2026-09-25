"""Generate structured answers through a fixed local Ollama connection.

Contents:
    - Runtime/model constants and response_schema define the supported setup.
    - LocalGenerator performs bounded HTTP reads and local-model preflight.
    - generate submits one chat request and returns text for shared validation.

Only 127.0.0.1:11434 is contacted. http.client ignores proxy environment variables
and never follows redirects. Normal answering has no pull, cloud, tool, or retry
path. A local daemon is still a separate trusted process; start it with cloud
features disabled and verify external-network isolation during integration.
"""

import http.client
import json
import logging
import math
import os
from time import monotonic

from .answering import (
    AnswerError, Context, MAX_CLAIMS, MAX_CLAIM_CHARS, QUESTION_CHARS,
    RESPONSE_CHARS, SYSTEM_PROMPT,
)

DEFAULT_MODEL = "qwen2.5:1.5b"
# The single model allowlist prevents cloud aliases and untested model changes.
# The installed manifest digest must also match the verified download.
MODEL_DIGEST = "65ec06548149b04c096a120e4a6da9d4017ea809c91734ea5631e89f96ddc57b"
HOST = "127.0.0.1"
PORT = 11434
TIMEOUT_SECONDS = 120.0
CONTEXT_TOKENS = 16_384
OUTPUT_TOKENS = 512
HTTP_BYTES = 1_000_000
logger = logging.getLogger(__name__)


def response_schema(context: Context) -> dict:
    """Constrain output shape and citation choices; Python rechecks all of it."""
    return {
        "type": "object", "additionalProperties": False,
        "required": ["status", "claims"],
        "properties": {
            "status": {"type": "string", "enum": ["answered", "insufficient_evidence"]},
            "claims": {"type": "array", "maxItems": MAX_CLAIMS, "items": {
                "type": "object", "additionalProperties": False,
                "required": ["text", "citations"],
                "properties": {
                    "text": {"type": "string", "minLength": 1, "maxLength": MAX_CLAIM_CHARS},
                    "citations": {"type": "array", "minItems": 1, "uniqueItems": True,
                                  "items": {"type": "string", "enum": [p.id for p in context.passages]}},
                },
            }},
        },
    }


class LocalGenerator:
    """Lazy adapter requiring an already running daemon and installed model."""

    def __init__(self, model: str | None = None, timeout: float = TIMEOUT_SECONDS):
        """Read only the local model setting; never read hosted credentials."""
        self.model = model if model is not None else os.environ.get("ASK_NOTES_LOCAL_MODEL", DEFAULT_MODEL)
        if self.model != DEFAULT_MODEL:
            raise AnswerError(f"This milestone supports only local {DEFAULT_MODEL}; unset or correct ASK_NOTES_LOCAL_MODEL.")
        if not math.isfinite(timeout) or not 0 < timeout <= TIMEOUT_SECONDS:
            raise ValueError(f"Timeout must be positive and at most {TIMEOUT_SECONDS:g} seconds.")
        self.timeout = timeout
        self.metadata = {}

    def _request(self, path: str, payload: dict | None, deadline: float) -> dict:
        """Make one fixed-host request under a shared deadline and byte ceiling.

        Read a bounded amount at a time and update the socket timeout so a slow
        response cannot reset the whole request's deadline on every chunk.
        Do not expose response bodies or low-level exception strings in errors.
        """
        remaining = deadline - monotonic()
        if remaining <= 0:
            raise AnswerError("Local generation timed out; check Ollama and available memory.")
        connection = http.client.HTTPConnection(HOST, PORT, timeout=remaining)
        try:
            body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
            connection.request("GET" if body is None else "POST", path, body,
                               {"Content-Type": "application/json"})
            response = connection.getresponse()
            if response.status != 200:
                # Ignore the untrusted body, which can contain prompts or paths.
                if response.status == 404:
                    raise AnswerError(f"Local model unavailable. Install it explicitly: ollama pull {DEFAULT_MODEL}")
                raise AnswerError(f"Local runtime returned HTTP {response.status}; check model setup, context, and memory. No retry was made.")
            data = bytearray()
            while True:
                remaining = deadline - monotonic()
                if remaining <= 0:
                    raise TimeoutError
                # The response may own the socket after a Connection: close.
                if connection.sock is not None:
                    connection.sock.settimeout(remaining)
                elif response.fp is not None and hasattr(response.fp, "raw"):
                    response.fp.raw._sock.settimeout(remaining)
                block = response.read1(min(65_536, HTTP_BYTES + 1 - len(data)))
                if not block:
                    break
                data.extend(block)
                if len(data) > HTTP_BYTES:
                    raise AnswerError("Local runtime response exceeded the byte limit.")
            value = json.loads(data)
            if not isinstance(value, dict) or "error" in value:
                raise ValueError("invalid runtime response")
            return value
        except TimeoutError as exc:
            raise AnswerError("Local generation timed out; check Ollama and available memory.") from exc
        except (OSError, http.client.HTTPException) as exc:
            raise AnswerError("Cannot reach local Ollama at 127.0.0.1:11434. Start it with OLLAMA_NO_CLOUD=1 ollama serve; see README local setup.") from exc
        except (ValueError, UnicodeError, RecursionError) as exc:
            raise AnswerError("Local runtime returned malformed JSON; no answer was displayed.") from exc
        finally:
            connection.close()

    def generate(self, question: str, context: Context) -> str:
        """Validate local assets, then make exactly one nonstreaming chat request."""
        if not question.strip() or len(question) > QUESTION_CHARS or not context.passages:
            raise AnswerError("Generation requires a bounded question and nonempty evidence.")
        schema = response_schema(context)
        # Embedding/context JSON is not interpolated into instruction strings.
        user = json.dumps({"question": question, "evidence": json.loads(context.serialized)}, ensure_ascii=False)
        # Qwen's byte-level tokenizer uses no more tokens than UTF-8 bytes for
        # ordinary text. Reserve schema bytes, template margin, and output so
        # the runtime cannot quietly drop old evidence when context is full.
        input_bound = sum(len(text.encode("utf-8")) for text in (SYSTEM_PROMPT, user, json.dumps(schema)))
        if input_bound + OUTPUT_TOKENS + 1024 > CONTEXT_TOKENS:
            raise AnswerError("Input exceeds the local model's conservative context bound; reduce --context-chars or shorten the question.")
        deadline = monotonic() + self.timeout
        tags = self._request("/api/tags", None, deadline)
        models = tags.get("models")
        if not isinstance(models, list):
            raise AnswerError("Local runtime returned an invalid model list.")
        installed = next((item for item in models if isinstance(item, dict) and item.get("name") == self.model), None)
        if installed is None:
            raise AnswerError(f"Local model is missing. Download it during setup: ollama pull {DEFAULT_MODEL}")
        details = installed.get("details", {})
        if not isinstance(details, dict) or details.get("format") != "gguf" or details.get("family") != "qwen2":
            raise AnswerError("Expected local Qwen GGUF weights; remote or incompatible models are rejected.")
        if installed.get("digest") != MODEL_DIGEST:
            raise AnswerError("Installed model digest differs from the tested local model; restore the documented model assets.")
        show = self._request("/api/show", {"model": self.model}, deadline)
        if show.get("remote_host") or show.get("remote_model"):
            raise AnswerError("Cloud-backed models are not allowed for local answers.")
        version = self._request("/api/version", None, deadline)
        self.metadata = {"model": self.model, "digest": installed.get("digest"),
                         "runtime_version": version.get("version"), "details": details,
                         "context_tokens": CONTEXT_TOKENS, "output_tokens": OUTPUT_TOKENS}
        logger.debug("Local generator: model=%s digest=%s runtime=%s", self.model,
                     self.metadata["digest"], self.metadata["runtime_version"])
        result = self._request("/api/chat", {
            "model": self.model,
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user}],
            "format": schema, "stream": False,
            # Release the small Mac's model memory immediately after this answer.
            "keep_alive": 0,
            "options": {"temperature": 0, "seed": 0, "num_ctx": CONTEXT_TOKENS,
                        "num_predict": OUTPUT_TOKENS},
        }, deadline)
        message = result.get("message")
        if result.get("done") is not True or result.get("done_reason") != "stop" or not isinstance(message, dict):
            raise AnswerError("Local model did not finish a complete answer; no partial output was displayed.")
        raw = message.get("content")
        if message.get("tool_calls") or not isinstance(raw, str) or len(raw) > RESPONSE_CHARS:
            raise AnswerError("Local model returned unsupported or oversized output.")
        self.metadata.update({key: result.get(key) for key in (
            "prompt_eval_count", "eval_count", "total_duration", "load_duration",
        )})
        return raw
