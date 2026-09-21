# Retrieval

## Contents

- [Retrieval](#retrieval)
- [How retrieval works](#how-retrieval-works)

## How retrieval works

Retrieval finds useful passages from a larger collection of documents. A keyword retriever looks for words shared by the question and each passage. A future semantic retriever can find related ideas even when the exact words differ.

The usual retrieval pipeline is loading documents, splitting them into chunks, indexing the chunks, and ranking the chunks for a query. Overlapping chunks reduce the chance that an important sentence is separated from the context around it.