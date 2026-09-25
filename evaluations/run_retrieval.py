"""Compare all three retrievers on fixed evidence-phrase labels.

Contents:
    - ``CASES`` preserves the original 23 questions and labels unchanged.
    - ``rank_change`` compares answer positions at an explicit cutoff.
    - ``render_report`` explains metrics, evidence, and the JSON schema.
    - ``main`` runs offline retrieval and writes separate hybrid artifacts.

Run: .venv-semantic/bin/python -m evaluations.run_retrieval
The historical results.json and original question labels are never overwritten.
"""

import hashlib
import importlib.metadata
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

from src.chunker import chunk_documents
from src.hybrid import HybridRetriever, RRF_CONSTANT
from src.loader import load_documents
from src.semantic import MODEL_ID, MODEL_REVISION

# Multiple phrases permit equivalent evidence in overlapping or repeated passages.
CASES = [
    ('What does a keyword retriever look for?', 'retrieval.md', ['words shared by the question and each passage']),
    ('Why do neighboring text segments repeat some of their content?', 'retrieval.md', ['Overlapping chunks reduce the chance']),
    ('How can related ideas be found when the wording is different?', 'retrieval.md', ['even when the exact words differ']),
    ('What are the steps in the retrieval pipeline?', 'retrieval.md', ['loading documents, splitting them into chunks']),
    ('What do type hints help explain?', 'python.txt', ['expected inputs and outputs']),
    ('How many responsibilities should a function have?', 'python.txt', ['one clear responsibility']),
    ('Can I verify a retriever without an online service?', 'python.txt', ['without requiring a web service']),
    ('What acts as runnable examples of program behavior?', 'python.txt', ['Tests are executable examples']),
    ('What was Li Jingsui originally called?', 'History.md', ['né Xu Jingsui']),
    ('Who was Li Jingsui\'s mother?', 'History.md', ['His mother was Xu Zhigao\'s second wife Lady Song Fujin']),
    ('Why did Xu Jingsui replace his brother as junior regent?', 'History.md', ['Xu Jingqian fell ill']),
    ('When did Xu Zhigao change his name to Li Bian?', 'History.md', ['In 939, Xu Zhigao changed']),
    ('Why did Li Jingsui choose the courtesy name Tuishen?', 'History.md', ['to show his lack of desire to be heir']),
    ('How did Li Jingsui react when Zhang Yi broke his jade cup?', 'History.md', ['Instead of becoming angry, Li Jingsui apologized']),
    ('How was Li Jingsui poisoned after playing polo?', 'History.md', ['Yuan gave him milk laced with poison']),
    ('What was Judy Garland\'s birth name?', 'History.md', ['born Frances Ethel Gumm']),
    ('Where was Judy Garland born?', 'History.md', ['in Grand Rapids, Minnesota']),
    ('Which role brought Judy Garland international recognition?', 'History.md', ['international recognition for her portrayal of Dorothy Gale']),
    ('Which live album made Garland the first woman to win Album of the Year?', 'History.md', ['Her live album, Judy at Carnegie Hall (1961)']),
    ('What song did Garland sing during her first appearance at age two?', 'History.md', ['Christmas show to sing a chorus of "Jingle Bells."']),
    ('How do I reset my email password?', None, []),
    ('What temperature should I bake sourdough bread at?', None, []),
    ('How do I replace a bicycle tire?', None, []),
]



def rank_change(hybrid_rank, baseline_rank, cutoff=3):
    """Compare first-answer ranks within a cutoff, treating all misses equally.

    A move outside the displayed top three is not a top-three improvement.
    Keeping the cutoff explicit also distinguishes a top-one hit change from
    merely moving a lower-ranked answer within the first three results.
    """
    hybrid = hybrid_rank if hybrid_rank is not None and hybrid_rank <= cutoff else cutoff + 1
    baseline = baseline_rank if baseline_rank is not None and baseline_rank <= cutoff else cutoff + 1
    return "gain" if hybrid < baseline else "regression" if hybrid > baseline else "tie"


def render_report(report):
    """Render a reviewable summary; JSON retains raw scores and full passages."""
    lines = ["# Hybrid retrieval evaluation", "", "## Contents", "",
             "- [Setup](#setup)", "- [Metrics](#metrics)",
             "- [Per-query comparison](#per-query-comparison)",
             "- [Result schema and interpretation](#result-schema-and-interpretation)", "",
             "## Setup", "",
             "The original 23 questions and evidence-phrase labels are unchanged: 20 answerable and 3 unrelated. "
             "All modes use identical 120-word chunks with 20-word overlap. A hit requires the labeled evidence "
             "inside a returned chunk, not just the expected filename. This is a diagnostic set, not a general benchmark.", "",
             f"Run: `{report['command']}`. The pinned model cache must be populated first; inference is offline. "
             f"This run used {report['chunks']} chunks, RRF constant {RRF_CONSTANT}, and full eligible-corpus branch rankings. "
             "[hybrid-results.json](hybrid-results.json) records corpus hashes, model revision, versions, and complete top-result evidence. "
             "[results.json](results.json) remains the historical two-mode run.", "",
             "## Metrics", "", "| Method | Hit@1 | Hit@3 | Unrelated returning results |",
             "| --- | --- | --- | --- |"]
    for name, metrics in report['metrics'].items():
        lines.append(f"| {name} | {metrics['hit_at_1']:.0%} | {metrics['hit_at_3']:.0%} | "
                     f"{metrics['unrelated_queries_returning_results']}/{metrics['unrelated_queries']} |")
    lines.extend(["", "## Per-query comparison", "",
                  "Ranks below are the first labeled answer in the top three; — is a top-three miss. "
                  "Changes compare rank positions within the top three, treating all misses equally. "
                  "Unrelated questions have no expected answer and are excluded from gain/regression counts.", "",
                  "| Question | Keyword | Semantic | Hybrid | vs keyword | vs semantic |",
                  "| --- | --- | --- | --- | --- | --- |"])
    for row in report['results']:
        ranks = [str(row[name + '_rank'] or '—') for name in ('keyword', 'semantic', 'hybrid')]
        changes = [row['changes'][name]['top3'] if row['expected_chunks'] else 'n/a'
                   for name in ('keyword', 'semantic')]
        lines.append('| ' + ' | '.join([row['query'], *ranks, *changes]) + ' |')
    lines.extend(["", "## Result schema and interpretation", "",
                  "JSON `contents` describes its sections. Top-level metadata records model identity, versions, "
                  "timestamp, corpus hashes, settings, and reproduction command. `results` contains labels, expected "
                  "chunk identities, all three methods’ top-three passages/scores, and full first-answer ranks. "
                  "Each hybrid result includes `keyword_rank` and `semantic_rank` in the full branch lists; null means absent. "
                  "`changes` reports top-one and top-three gains/ties/regressions against each baseline. "
                  "`metrics` excludes unrelated queries from the hit denominators.", "",
                  "RRF combines ranks, not score magnitudes. With full semantic rankings, every literal match receives "
                  "two contributions; this can promote a weak keyword hit above relevant semantic-only evidence. "
                  "No relevance threshold or automatic fallback exists. Unrelated questions still return neighbors. "
                  "Hybrid remains opt-in whether or not these aggregate results improve.", ""])
    return '\n'.join(lines)


def main():
    """Evaluate one corpus snapshot, preserving historical output and fixed labels."""
    root = Path(__file__).resolve().parents[1]
    documents = load_documents(root / 'documents')
    chunks = chunk_documents(documents, chunk_size=120, overlap=20)
    labeled = []
    for query, source, phrases in CASES:
        expected = [(c.source, c.chunk_number) for c in chunks if c.source == source
                    and any(p in c.text for p in phrases)]
        if source and not expected:
            raise ValueError(f'Evidence missing or split across chunks: {query}')
        labeled.append((query, source, phrases, expected))

    hybrid = HybridRetriever(chunks, offline=True, cache=root / '.cache/ask-my-notes/models')
    # Sharing the existing branch instances avoids loading a second model; each
    # method still runs its public search path and all use the identical chunks.
    retrievers = {'keyword': hybrid.keyword, 'semantic': hybrid.semantic, 'hybrid': hybrid}
    report = {
        'contents': {'metadata': 'Top-level run configuration, environment, and corpus hashes',
                     'results': 'Per-query evidence labels, top passages, full answer ranks, and changes',
                     'metrics': 'Answerable Hit@1/Hit@3 and separate unrelated-return counts'},
        'explanation': 'Fixed labels; full-corpus equal-weight RRF. Scores across methods are not comparable.',
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'command': '.venv-semantic/bin/python -m evaluations.run_retrieval',
        'model': MODEL_ID, 'revision': MODEL_REVISION, 'offline': True,
        'python': platform.python_version(), 'platform': platform.platform(),
        'versions': {name: importlib.metadata.version(name) for name in (
            'sentence-transformers', 'torch', 'transformers', 'huggingface-hub', 'numpy')},
        'chunk_size': 120, 'overlap': 20, 'chunks': len(hybrid.chunks),
        'rrf_constant': RRF_CONSTANT, 'candidate_depth': 'all unique nonblank chunks in each branch',
        'corpus_sha256': {d.source: hashlib.sha256(d.text.encode()).hexdigest() for d in documents},
        'results': [], 'metrics': {},
    }
    for query, source, phrases, expected in labeled:
        row = {'query': query, 'evidence': phrases, 'expected_chunks': expected, 'changes': {}}
        branch_ranks = {}
        for name, retriever in retrievers.items():
            ranked = retriever.search(query, limit=len(hybrid.chunks))
            if name != 'hybrid':
                branch_ranks[name] = {(r.chunk.source, r.chunk.chunk_number): i
                                      for i, r in enumerate(ranked, 1)}
            row[name] = []
            for result in ranked[:3]:
                identity = (result.chunk.source, result.chunk.chunk_number)
                entry = {'source': identity[0], 'chunk': identity[1],
                         'score': result.score, 'text': result.chunk.text}
                if name == 'hybrid':
                    entry.update({method + '_rank': ranks.get(identity)
                                  for method, ranks in branch_ranks.items()})
                row[name].append(entry)
            full_rank = next((i for i, r in enumerate(ranked, 1)
                              if (r.chunk.source, r.chunk.chunk_number) in expected), None)
            row[name + '_full_rank'] = full_rank
            row[name + '_rank'] = full_rank if full_rank is not None and full_rank <= 3 else None
        if expected:
            row['changes'] = {name: {f'top{cutoff}': rank_change(
                row['hybrid_full_rank'], row[name + '_full_rank'], cutoff)
                for cutoff in (1, 3)} for name in ('keyword', 'semantic')}
        report['results'].append(row)

    answerable = [r for r in report['results'] if r['expected_chunks']]
    unrelated = [r for r in report['results'] if not r['expected_chunks']]
    for name in retrievers:
        report['metrics'][name] = {
            'answerable_queries': len(answerable),
            'hit_at_1': sum(r[name + '_rank'] == 1 for r in answerable) / len(answerable),
            'hit_at_3': sum(r[name + '_rank'] is not None for r in answerable) / len(answerable),
            'unrelated_queries_returning_results': sum(bool(r[name]) for r in unrelated),
            'unrelated_queries': len(unrelated),
        }
    # New artifact names deliberately preserve the original two-method evidence.
    (root / 'evaluations/hybrid-results.json').write_text(json.dumps(report, indent=2) + '\n')
    (root / 'evaluations/hybrid-results.md').write_text(render_report(report))
    print(json.dumps(report['metrics'], indent=2))


if __name__ == '__main__':
    main()
