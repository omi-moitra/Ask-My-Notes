"""Tests for recursive supported-file loading.

Contents:
        - ``test_loader_finds_supported_files_recursively`` checks filtering and
            relative source metadata.
"""

from src.loader import load_documents


def test_loader_finds_supported_files_recursively(tmp_path):
    """Load nested Markdown while ignoring unsupported extensions."""
    # Build a miniature directory tree that exercises recursion.
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "note.md").write_text("hello", encoding="utf-8")
    (tmp_path / "ignore.csv").write_text("hello", encoding="utf-8")

    # Run the public loader rather than reaching into its implementation.
    documents = load_documents(tmp_path)

    # The relative path is the metadata used later in search output.
    assert [(document.source, document.text) for document in documents] == [("nested/note.md", "hello")]