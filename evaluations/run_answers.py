"""Evaluate local answers on fixed synthetic notes without altering retrieval baselines.

Contents:
    - evaluate_case records evidence, validated answers, and diagnostic outcomes.
    - render_report produces a readable companion with manual review criteria.
    - main reuses one cached encoder and writes separate local-answer artifacts.

Run explicitly: .venv-semantic/bin/python -m evaluations.run_answers
Requires cached embeddings and a running local Ollama with the pinned model.
Automated status/citation checks are not substitutes for manual factual review.
"""

from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
from time import monotonic

from .answer_cases import CASES
from src.answering import AnswerError, CONTEXT_CHARS, SYSTEM_PROMPT, answer_question
from src.chunker import chunk_documents
from src.local_generator import DEFAULT_MODEL, MODEL_DIGEST, LocalGenerator
from src.models import Document
from src.semantic import MODEL_ID, MODEL_REVISION, SemanticRetriever, SentenceTransformerEncoder


def evaluate_case(case, encoder):
    """Preserve labels and failures while exposing exactly what the model saw."""
    documents = [Document(source, text) for source, text in case["notes"].items()]
    retriever = SemanticRetriever(chunk_documents(documents), encoder=encoder)
    generator = LocalGenerator()
    # Keep the common workflow intact; record its input at the generator boundary.
    captured = {}
    class RecordingGenerator:
        """Delegate one generation while retaining context for failed responses."""
        def generate(self, question, context):
            """Capture evidence, never credentials or runtime response fragments."""
            captured["context"] = context
            return generator.generate(question, context)
    row = {**case, "corpus_sha256": {d.source: hashlib.sha256(d.text.encode()).hexdigest() for d in documents}}
    start = monotonic()
    try:
        answer = answer_question(case["question"], retriever, RecordingGenerator())
        row.update(status=answer.status, claims=[asdict(c) for c in answer.claims], error=None)
        cited = {identifier for c in answer.claims for identifier in c.citations}
        cited_sources = {p.chunk.source for p in answer.context.passages if p.id in cited}
        row["required_sources_cited"] = set(case["required_sources"]) <= cited_sources
        row["citation_structure_valid"] = True
    except AnswerError as exc:
        row.update(status="error", claims=[], error=str(exc),
                   required_sources_cited=False, citation_structure_valid=False)
    context = captured.get("context")
    row["context"] = json.loads(context.serialized) if context else []
    row["retrieval_coverage"] = set(case["required_sources"]) <= {p["source"] for p in row["context"]}
    row["status_matches_expectation"] = row["status"] == case["expected_status"]
    row["elapsed_seconds"] = round(monotonic() - start, 3)
    row["runtime"] = generator.metadata
    return row


def render_report(report):
    """Expose claims, citations, and label criteria for a separate human review."""
    lines = ["# Local answer evaluation", "", "## Contents", "",
             "- [Setup](#setup)", "- [Diagnostic counts](#diagnostic-counts)",
             "- [Case results](#case-results)", "- [Schema and interpretation](#schema-and-interpretation)",
             "", "## Setup", "", f"Run: {report['created_utc']}. Model: `{DEFAULT_MODEL}`; manifest `{MODEL_DIGEST}`.",
             "", "Reproduce: `.venv-semantic/bin/python -m evaluations.run_answers` with cached embeddings and local Ollama running.",
             "", "Each case has a separate synthetic collection. Semantic retrieval uses 120-word chunks, overlap 20, and top three. Labels were fixed before execution.",
             "", "## Diagnostic counts", ""]
    lines.extend(f"- {key}: {value}" for key, value in report["metrics"].items())
    lines += ["", "These counts check behavior and provenance, not factual correctness. See [manual review](local-answer-review.md) for claim-support judgments.",
              "", "## Case results", ""]
    for row in report["cases"]:
        lines += [f"### {row['id']}", "", f"**Question:** {row['question']}", "",
                  f"**Expected:** {row['expected_status']}. {row['review_criteria']}", "",
                  f"**Observed:** {row['status']}; {row['elapsed_seconds']} seconds.", ""]
        for claim in row["claims"]:
            lines.append(f"- {claim['text']} ({', '.join(claim['citations'])})")
        if row["error"]:
            lines.append(f"Error: {row['error']}")
        lines += ["", "Evidence supplied:", ""]
        for passage in row["context"]:
            lines += [f"- {passage['id']}: `{passage['source']}` chunk {passage['chunk_number']}: {passage['text']}"]
        lines.append("")
    lines += ["## Schema and interpretation", "",
              "The JSON includes contents/explanation metadata, versions, fixed labels, corpus hashes, exact supplied evidence, claims, citation IDs, runtime usage, failures, and latency. Retrieval coverage checks required source presence; citation structure checks known identifiers. Neither proves claim support. Abstentions on answerable questions and unsupported answers on unanswerable questions are separate. This eight-case diagnostic is not a general benchmark.", ""]
    return "\n".join(lines)


def main():
    """Write new artifacts only; leave historical retrieval results untouched."""
    encoder = SentenceTransformerEncoder(offline=True)
    rows = [evaluate_case(case, encoder) for case in CASES]
    answerable = [r for r in rows if r["expected_status"] == "answered"]
    unanswerable = [r for r in rows if r["expected_status"] == "insufficient_evidence"]
    report = {
        "contents": {"configuration": "Reproducible local settings", "metrics": "Diagnostic counts, not truth scores",
                     "cases": "Fixed labels, original notes, supplied context, and observed answers"},
        "explanation": "Synthetic local RAG evaluation. Human review is separate; do not interpret citation validity as factual support.",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "configuration": {"python": platform.python_version(), "platform": platform.platform(),
            "embedding_model": MODEL_ID, "embedding_revision": MODEL_REVISION,
            "prompt_sha256": hashlib.sha256(SYSTEM_PROMPT.encode()).hexdigest(),
            "fixture_sha256": hashlib.sha256(Path(__file__).with_name("answer_cases.py").read_bytes()).hexdigest(),
            "generation_model": DEFAULT_MODEL, "generation_digest": MODEL_DIGEST,
            "chunk_size": 120, "overlap": 20, "limit": 3, "context_chars": CONTEXT_CHARS,
            "retrieval_offline": True,
            "packages": {p: importlib.metadata.version(p) for p in ("sentence-transformers", "torch", "transformers")}},
        "metrics": {"cases": len(rows), "answerable": len(answerable), "unanswerable": len(unanswerable),
            "errors": sum(r["status"] == "error" for r in rows),
            "status_matches": sum(r["status_matches_expectation"] for r in rows),
            "valid_response_structures": sum(r["citation_structure_valid"] for r in rows),
            "answerable_retrieval_coverage": sum(r["retrieval_coverage"] for r in answerable),
            "answerable_abstentions": sum(r["status"] == "insufficient_evidence" for r in answerable),
            "unanswerable_answered": sum(r["status"] == "answered" for r in unanswerable)},
        "cases": rows,
    }
    destination = Path(__file__).parent
    (destination / "local-answer-results.json").write_text(json.dumps(report, indent=2) + "\n")
    (destination / "local-answer-results.md").write_text(render_report(report))
    print(json.dumps(report["metrics"], indent=2))


if __name__ == "__main__":
    main()
