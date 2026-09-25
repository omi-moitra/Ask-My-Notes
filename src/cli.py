"""Command-line entry point for Ask My Notes.

Contents:
    - ``build_parser`` defines the user-facing command and options.
    - ``run_ask`` handles bounded local generation and expected answer failures.
    - ``main`` connects loading, chunking, retrieval, and formatted output.
"""

import argparse
import logging
from pathlib import Path

from .answering import (AnswerError, CONTEXT_CHARS, MAX_PASSAGES, QUESTION_CHARS,
                        answer_question, render_answer)
from .local_generator import LocalGenerator
from .chunker import chunk_documents
from .hybrid import HybridRetriever
from .loader import load_documents
from .search import KeywordRetriever
from .semantic import DEFAULT_MODEL_CACHE, MODEL_ID, MODEL_REVISION, SemanticError, SemanticRetriever


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser used by ``main``.

    Global options configure ingestion and chunking; the ``search`` subcommand
    owns query-specific options such as the result limit.
    """
    parser = argparse.ArgumentParser(description="Search local Markdown and text notes.")
    # These options apply before the subcommand and configure the collection.
    parser.add_argument("--documents", type=Path, default=Path("documents"), help="Documents directory")
    parser.add_argument("--chunk-size", type=int, default=120, help="Words per chunk")
    parser.add_argument("--overlap", type=int, default=20, help="Overlapping words")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    subparsers = parser.add_subparsers(dest="command", required=True)
    # Keep the first milestone extensible by grouping search under a subcommand.
    search_parser = subparsers.add_parser("search", help="Search the document collection")
    search_parser.add_argument("query", help="Search terms or a question")
    search_parser.add_argument("--limit", type=int, default=3, help="Number of passages to print")
    search_parser.add_argument("--retriever", choices=("keyword", "semantic", "hybrid"), default="keyword",
                               help="Ranking method (default: keyword)")
    # None distinguishes an explicitly supplied cache from the semantic default.
    search_parser.add_argument("--model-cache", type=Path, help="Model cache for semantic or hybrid search")
    search_parser.add_argument("--offline", action="store_true", help="Use cached model assets only (semantic/hybrid)")
    # ask is separate so search keeps its historical defaults and flags.
    ask_parser = subparsers.add_parser("ask", help="Answer from notes using a local model")
    ask_parser.add_argument("query", help="Question to answer from the supplied notes")
    ask_parser.add_argument("--limit", type=int, default=3, help="Candidate passages (1–20)")
    ask_parser.add_argument("--retriever", choices=("keyword", "semantic", "hybrid"), default="semantic",
                            help="Evidence ranking (default: semantic; requires semantic extra)")
    ask_parser.add_argument("--model-cache", type=Path, help="Embedding model cache (semantic/hybrid)")
    ask_parser.add_argument("--retrieval-offline", dest="offline", action="store_true",
                            help="Use cached embeddings only; answer generation is always local")
    ask_parser.add_argument("--context-chars", type=int, default=CONTEXT_CHARS,
                            help="Serialized evidence budget, including metadata (2–12000)")
    return parser


def run_ask(args) -> int:
    """Build one answer without exposing partial output or swallowing bugs."""
    try:
        documents = load_documents(args.documents)
        if not documents:
            logging.error("No .txt or .md files found in %s", args.documents)
            return 1
        chunks = chunk_documents(documents, args.chunk_size, args.overlap)
        if args.retriever == "keyword":
            retriever = KeywordRetriever(chunks)
        else:
            retriever_type = HybridRetriever if args.retriever == "hybrid" else SemanticRetriever
            retriever = retriever_type(chunks, cache=args.model_cache or DEFAULT_MODEL_CACHE, offline=args.offline)
        # Construction is model-free; empty retrieval never contacts the daemon.
        answer = answer_question(args.query, retriever, LocalGenerator(), args.limit, args.context_chars)
        print(render_answer(answer))
        return 0
    except (AnswerError, SemanticError) as exc:
        logging.error("%s", exc)
        return 1
    except (OSError, UnicodeError):
        # Keep filesystem errors concise without exposing low-level internals.
        logging.error("Cannot read the notes collection; check its path and permissions.")
        return 1


def main() -> int:
    """Run the complete search workflow and return a shell exit code.

    The steps are: parse arguments, configure logging, load files, create
    chunks, rank the query, and print each result with its source metadata.
    """
    # Parse first so invalid user input receives argparse's standard feedback.
    parser = build_parser()
    args = parser.parse_args()
    if args.retriever == "keyword" and (args.model_cache is not None or args.offline):
        flag = "--retrieval-offline" if args.command == "ask" else "--offline"
        parser.error(f"--model-cache and {flag} require --retriever semantic or hybrid")
    if args.command == "ask":
        if not args.query.strip() or len(args.query) > QUESTION_CHARS:
            parser.error(f"ask requires a nonblank question of at most {QUESTION_CHARS} characters")
        if not 1 <= args.limit <= MAX_PASSAGES:
            parser.error(f"ask --limit must be between 1 and {MAX_PASSAGES}")
        if not 2 <= args.context_chars <= CONTEXT_CHARS:
            parser.error(f"--context-chars must be between 2 and {CONTEXT_CHARS}")
        if args.chunk_size <= 0 or not 0 <= args.overlap < args.chunk_size:
            parser.error("ask requires positive --chunk-size and 0 <= --overlap < --chunk-size")
    # Logging stays quiet by default but can expose loading details on demand.
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(levelname)s: %(message)s")
    if args.command == "ask":
        return run_ask(args)
    # Loading happens at runtime so edits to documents are reflected per search.
    documents = load_documents(args.documents)
    # A missing collection is a user-facing setup problem, not a crash.
    if not documents:
        print(f"No .txt or .md files found in {args.documents}")
        return 1

    # Chunking is separate from loading so future loaders can reuse it.
    chunks = chunk_documents(documents, args.chunk_size, args.overlap)
    # Selection stays at the boundary; all implementations return the same
    # passage/score records, so rendering does not depend on model internals.
    logging.debug("Retriever: %s", args.retriever)
    if args.retriever in ("semantic", "hybrid"):
        cache = args.model_cache if args.model_cache is not None else DEFAULT_MODEL_CACHE
        logging.debug("Model: %s revision=%s cache=%s eligible_chunks=%d",
                      MODEL_ID, MODEL_REVISION, cache, sum(bool(c.text.strip()) for c in chunks))
        # Both model-backed modes share optional setup. Hybrid owns the keyword
        # and semantic branches, so the CLI still sees one search interface.
        retriever_type = HybridRetriever if args.retriever == "hybrid" else SemanticRetriever
        retriever = retriever_type(chunks, cache=cache, offline=args.offline)
    else:
        retriever = KeywordRetriever(chunks)
    try:
        results = retriever.search(args.query, args.limit)
    except SemanticError as exc:
        # Only expected semantic failures become concise CLI messages. Bugs and
        # existing ingestion/configuration exceptions retain their normal path.
        logging.error("%s", exc)
        return 1
    # No matches is a successful search with an empty result set.
    if not results:
        print("No matching passages found.")
        return 0

    # Print stable, citation-friendly metadata before each passage body.
    for index, result in enumerate(results, start=1):
        chunk = result.chunk
        print(f"{index}. [{result.score:.3f}] {chunk.source} (chunk {chunk.chunk_number})")
        print(f"   {chunk.text}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
