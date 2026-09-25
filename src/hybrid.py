"""Combine existing retrieval rankings without mixing their score scales.

Contents:
    - ``RRF_CONSTANT`` fixes the reciprocal-rank policy for this milestone.
    - ``fuse_rankings`` merges prepared lists by stable passage identity.
    - ``HybridRetriever`` snapshots chunks and reuses both branch indexes.

RRF rewards agreement, not verified relevance. With full semantic rankings,
weak keyword hits receive a second vote and can outrank semantic-only evidence.
"""

import logging
import math
from pathlib import Path
from typing import Sequence

from .models import DocumentChunk, Retriever, SearchResult
from .search import KeywordRetriever
from .semantic import DEFAULT_MODEL_CACHE, Encoder, SemanticRetriever

RRF_CONSTANT = 60
logger = logging.getLogger(__name__)


def fuse_rankings(keyword: Sequence[SearchResult], semantic: Sequence[SearchResult],
                  limit: int = 3) -> list[SearchResult]:
    """Fuse ordered lists using one-based ranks, ignoring raw score magnitudes.

    Identity is (source, chunk_number), not passage text. Repeated entries in a
    branch contribute only at their first position; later duplicates still take
    up positions in that supplied list. Conflicting text is always an error.
    """
    if limit <= 0:
        return []
    chunks: dict[tuple[str, int], DocumentChunk] = {}
    contributions: dict[tuple[str, int], list[float]] = {}
    for branch in (keyword, semantic):
        seen = set()
        for rank, result in enumerate(branch, start=1):
            chunk = result.chunk
            identity = (chunk.source, chunk.chunk_number)
            if identity in chunks and chunks[identity].text != chunk.text:
                raise ValueError(f"Conflicting text for chunk {identity!r}")
            if identity in seen:
                continue
            seen.add(identity)
            # The first original chunk remains the canonical display passage.
            chunks.setdefault(identity, chunk)
            contributions.setdefault(identity, []).append(1 / (RRF_CONSTANT + rank))

    fused = [SearchResult(chunks[key], math.fsum(values))
             for key, values in contributions.items()]
    # Sort before truncating. Rounding for display must not affect the result.
    return sorted(fused, key=lambda result: (
        -result.score, result.chunk.source, result.chunk.chunk_number,
    ))[:limit]


class HybridRetriever(Retriever):
    """Compose keyword and semantic retrieval over the same corpus snapshot."""

    def __init__(self, chunks: Sequence[DocumentChunk], encoder: Encoder | None = None,
                 *, cache: Path = DEFAULT_MODEL_CACHE, offline: bool = False):
        """Validate identity, copy the collection, and prepare model-free branches.

        Keyword receives a private list, while semantic snapshots the tuple.
        This protects both indexes from subsequent edits to the caller's list.
        Constructing semantic retrieval does not load its optional model stack.
        """
        canonical: dict[tuple[str, int], DocumentChunk] = {}
        for chunk in chunks:
            identity = (chunk.source, chunk.chunk_number)
            if identity in canonical and canonical[identity].text != chunk.text:
                raise ValueError(f"Conflicting text for chunk {identity!r}")
            canonical.setdefault(identity, chunk)
        self.chunks = tuple(chunk for chunk in canonical.values() if chunk.text.strip())
        self.keyword = KeywordRetriever(list(self.chunks))
        self.semantic = SemanticRetriever(self.chunks, encoder=encoder, cache=cache, offline=offline)

    def search(self, query: str, limit: int = 3) -> list[SearchResult]:
        """Rank the full candidate union, then limit the fused output.

        Both branches use N, the unique eligible corpus size, not the user's
        display limit. This makes smaller outputs prefixes of larger ones and
        preserves candidates that may rise after two contributions are added.
        Semantic errors propagate: a partial keyword list is not a fallback.
        """
        if limit <= 0 or not query.strip() or not self.chunks:
            return []
        candidate_count = len(self.chunks)
        keyword = self.keyword.search(query, limit=candidate_count)
        semantic = self.semantic.search(query, limit=candidate_count)
        logger.debug("Hybrid RRF: constant=%d eligible_chunks=%d keyword_results=%d semantic_results=%d",
                     RRF_CONSTANT, candidate_count, len(keyword), len(semantic))
        return fuse_rankings(keyword, semantic, limit)
