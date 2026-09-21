"""Load supported text documents from a directory tree.

Contents:
    - Constants describing supported file suffixes.
    - ``load_documents`` for recursive, UTF-8 document loading.
"""

import logging
from pathlib import Path

from .models import Document

LOGGER = logging.getLogger(__name__)
SUPPORTED_SUFFIXES = {".md", ".txt"}


def load_documents(directory: Path) -> list[Document]:
    """Recursively load non-empty Markdown and text files.

    The function walks the directory, ignores unsupported entries, decodes
    supported files as UTF-8, and returns paths relative to ``directory``.
    """
    documents: list[Document] = []
    # Sorting makes indexing and test results deterministic across filesystems.
    for path in sorted(directory.rglob("*")):
        # Directories and formats outside the milestone are not documents.
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_SUFFIXES:
            continue

        # Read the whole small local note so chunking can decide its boundaries.
        text = path.read_text(encoding="utf-8")
        # Empty files do not provide a useful searchable passage.
        if text.strip():
            documents.append(Document(source=path.relative_to(directory).as_posix(), text=text))
            LOGGER.debug("Loaded %s", path)

    # This summary helps diagnose an empty or incorrectly configured collection.
    LOGGER.info("Loaded %d documents from %s", len(documents), directory)
    return documents