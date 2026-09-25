"""Local semantic retrieval with optional, lazily loaded model dependencies.

Contents:
    - Model constants and ``SemanticError`` define reproducible setup/failures.
    - ``Encoder`` and ``SentenceTransformerEncoder`` isolate model operations.
    - ``_normalize`` validates vectors before cosine arithmetic.
    - ``SemanticRetriever`` keeps a stable, reusable in-memory passage index.
"""

import logging
import math
from pathlib import Path
from typing import Protocol, Sequence

from .models import DocumentChunk, Retriever, SearchResult

MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
# Resolve once, rather than fetching a moving branch on every new installation.
MODEL_REVISION = "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
DEFAULT_MODEL_CACHE = Path(".cache/ask-my-notes/models")
logger = logging.getLogger(__name__)


class SemanticError(RuntimeError):
    """An expected dependency, model, or embedding error suitable for the CLI."""


class Encoder(Protocol):
    """The small boundary implemented by the real model and test doubles.

    Each input text must produce one numeric vector, in the same order.
    Encoders own tokenization; retrieval must never apply keyword filtering.
    """

    def encode(self, texts: Sequence[str]) -> Sequence[Sequence[float]]:
        """Encode original text, warning if the model truncates any input."""
        ...


class SentenceTransformerEncoder:
    """Load the pinned CPU model only when the first encoding is requested."""

    def __init__(self, cache: Path = DEFAULT_MODEL_CACHE, offline: bool = False):
        """Store setup without importing libraries, creating files, or networking."""
        self.cache = Path(cache)
        self.offline = offline
        self._model = None

    def _load(self):
        """Load assets once; local snapshot paths prevent remote model discovery."""
        if self._model is not None:
            return self._model
        try:
            # Import inside the adapter so keyword use and fake-encoder tests
            # need neither PyTorch nor the Sentence Transformers dependency.
            from sentence_transformers import SentenceTransformer
            from huggingface_hub import snapshot_download
        except ImportError as exc:
            raise SemanticError(
                "Semantic dependencies are missing or incompatible. Install with "
                "python -m pip install -e '.[semantic]'"
            ) from exc

        logger.info("Loading semantic model %s (%s); cache=%s; offline=%s",
                    MODEL_ID, MODEL_REVISION, self.cache, self.offline)
        try:
            # Resolve only already-cached files offline. Passing the local
            # snapshot to the model also prevents optional-file HTTP probes.
            model_path = MODEL_ID
            if self.offline:
                model_path = snapshot_download(
                    MODEL_ID, revision=MODEL_REVISION,
                    cache_dir=str(self.cache), local_files_only=True,
                )
            self._model = SentenceTransformer(
                model_path, revision=MODEL_REVISION, device="cpu",
                cache_folder=str(self.cache), local_files_only=self.offline,
                trust_remote_code=False,
            )
        except (OSError, RuntimeError, ValueError) as exc:
            # Hub HTTP/cache exceptions derive from OSError in the pinned stack.
            advice = (
                "Populate this same cache with an online semantic search first."
                if self.offline else "Check network access and cache permissions, then retry."
            )
            raise SemanticError(f"Could not load semantic model from {self.cache}. {advice}") from exc
        return self._model

    def encode(self, texts: Sequence[str]) -> Sequence[Sequence[float]]:
        """Check model-token lengths, then encode in bounded CPU batches."""
        model = self._load()
        try:
            # Measure with the actual tokenizer, including special tokens.
            # Word-based chunk sizes cannot predict word-piece expansion.
            for start in range(0, len(texts), 32):
                batch = list(texts[start:start + 32])
                tokens = model.tokenizer(batch, truncation=False, padding=False)
                truncated = sum(len(ids) > model.max_seq_length for ids in tokens["input_ids"])
                if truncated:
                    logger.warning(
                        "%d input(s) exceed the model limit of %d tokens and will be "
                        "truncated; unseen tails cannot affect similarity. Original text is displayed.",
                        truncated, model.max_seq_length,
                    )
            return model.encode(list(texts), batch_size=32, normalize_embeddings=True,
                                show_progress_bar=False, convert_to_numpy=True)
        except (OSError, RuntimeError, ValueError) as exc:
            raise SemanticError("Semantic encoding failed; check model assets and available memory.") from exc


def _normalize(vectors, expected: int, dimension: int | None = None) -> list[tuple[float, ...]]:
    """Reject invalid batches and return unit vectors without requiring NumPy.

    Scaling before taking the norm avoids overflow from large finite values.
    Validate even normalized model output: injected encoders must obey the same
    contract, and malformed vectors must never quietly corrupt result scores.
    """
    try:
        rows = list(vectors)
        if len(rows) != expected:
            raise ValueError("wrong number of vectors")
        result = []
        for row in rows:
            values = tuple(float(value) for value in row)
            if not values or any(not math.isfinite(value) for value in values):
                raise ValueError("empty or nonfinite vector")
            if dimension is None:
                dimension = len(values)
            if len(values) != dimension:
                raise ValueError("inconsistent vector dimensions")
            scale = max(abs(value) for value in values)
            if scale == 0:
                raise ValueError("zero-length vector")
            scaled = tuple(value / scale for value in values)
            norm = math.sqrt(math.fsum(value * value for value in scaled))
            result.append(tuple(value / norm for value in scaled))
        return result
    except (TypeError, ValueError, OverflowError) as exc:
        raise SemanticError(f"Invalid encoder output: {exc}.") from exc


class SemanticRetriever(Retriever):
    """Rank original chunks by cosine similarity, reusing passage embeddings."""

    def __init__(self, chunks: Sequence[DocumentChunk], encoder: Encoder | None = None,
                 *, cache: Path = DEFAULT_MODEL_CACHE, offline: bool = False):
        """Snapshot eligible chunks; postpone model loading and index building."""
        # Frozen chunks plus a tuple keep caller list edits from shifting the
        # association between vectors and source passages after construction.
        self.chunks = tuple(chunk for chunk in chunks if chunk.text.strip())
        self.encoder = encoder if encoder is not None else SentenceTransformerEncoder(cache, offline)
        self._vectors = None

    def search(self, query: str, limit: int = 3) -> list[SearchResult]:
        """Return nearest passages without imposing a relevance threshold.

        A nonblank query, even punctuation or stop words, reaches the model.
        Negative similarities remain valid results. Unlike keyword matching,
        nearest neighbors do not establish that relevant evidence exists.
        """
        if limit <= 0 or not query.strip() or not self.chunks:
            return []
        if self._vectors is None:
            vectors = self.encoder.encode([chunk.text for chunk in self.chunks])
            # Commit the cache only after the entire batch passes validation.
            self._vectors = _normalize(vectors, len(self.chunks))
        query_vector = _normalize(self.encoder.encode([query]), 1, len(self._vectors[0]))[0]
        results = []
        for chunk, vector in zip(self.chunks, self._vectors):
            score = math.fsum(a * b for a, b in zip(vector, query_vector))
            # Roundoff can otherwise place a theoretically unit cosine just
            # beyond [-1, 1]. Do not round away meaningful differences for sort.
            results.append(SearchResult(chunk, max(-1.0, min(1.0, score))))
        return sorted(results, key=lambda result: (
            -result.score, result.chunk.source, result.chunk.chunk_number,
        ))[:limit]
