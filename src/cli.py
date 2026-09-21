"""Command-line entry point for Ask My Notes.

Contents:
    - ``build_parser`` defines the user-facing command and options.
    - ``main`` connects loading, chunking, retrieval, and formatted output.
"""

import argparse
import logging
from pathlib import Path

from .chunker import chunk_documents
from .loader import load_documents
from .search import KeywordRetriever


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
    return parser


def main() -> int:
    """Run the complete search workflow and return a shell exit code.

    The steps are: parse arguments, configure logging, load files, create
    chunks, rank the query, and print each result with its source metadata.
    """
    # Parse first so invalid user input receives argparse's standard feedback.
    args = build_parser().parse_args()
    # Logging stays quiet by default but can expose loading details on demand.
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(levelname)s: %(message)s")
    # Loading happens at runtime so edits to documents are reflected per search.
    documents = load_documents(args.documents)
    # A missing collection is a user-facing setup problem, not a crash.
    if not documents:
        print(f"No .txt or .md files found in {args.documents}")
        return 1

    # Chunking is separate from loading so future loaders can reuse it.
    chunks = chunk_documents(documents, args.chunk_size, args.overlap)
    # The CLI depends on the Retriever contract rather than scoring internals.
    results = KeywordRetriever(chunks).search(args.query, args.limit)
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