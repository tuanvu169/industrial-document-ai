"""Retrieval + citation evaluation on a real question set.

Usage (from backend/):
    python -m app.evaluation.run_eval --project <uuid> --dataset ../data/eval/questions.jsonl [--k 5] [--with-answers]

Each JSONL line: {"question": "...", "type": "factual", "relevant": [{"filename": "a.pdf", "page": 3}]}
Unanswerable questions: "relevant": [] (excluded from Recall/MRR; with --with-answers they are only counted).
Faithfulness / Answer Relevancy need an LLM judge and are NOT implemented here.
"""
import argparse
import json
import statistics
import time
import uuid

from app.core.db import SessionLocal
from app.evaluation.metrics import citation_accuracy, recall_at_k, reciprocal_rank
from app.rag import pipeline
from app.rag.retriever import retrieve


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True, type=uuid.UUID)
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--with-answers", action="store_true", help="also call Gemini and score citation accuracy")
    args = ap.parse_args()

    items = [json.loads(line) for line in open(args.dataset, encoding="utf-8") if line.strip()]
    recalls, rrs, cites, latencies = [], [], [], []
    with SessionLocal() as db:
        for it in items:
            rel = {(r["filename"], r["page"]) for r in it.get("relevant", [])}
            t0 = time.perf_counter()
            if args.with_answers:
                res = pipeline.run(db, args.project, it["question"], [])
                chunks = res.retrieved
                if rel:
                    cites.append(citation_accuracy([(s.filename, s.page_number) for s in res.sources], rel))
            else:
                chunks = retrieve(db, args.project, it["question"], top_k=args.k)
            latencies.append(time.perf_counter() - t0)
            if rel:
                got = [(c.filename, c.page_number) for c in chunks]
                recalls.append(recall_at_k(got, rel, args.k))
                rrs.append(reciprocal_rank(got, rel))

    def mean(xs):
        return round(statistics.mean(xs), 3) if xs else None

    print(json.dumps({
        "questions": len(items), "answerable": len(recalls), f"recall@{args.k}": mean(recalls), "mrr": mean(rrs),
        "citation_accuracy": mean(cites), "latency_s_mean": mean(latencies),
        "latency_s_p95": round(sorted(latencies)[int(0.95 * (len(latencies) - 1))], 3) if latencies else None,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
