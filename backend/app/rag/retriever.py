import uuid
from collections import defaultdict
from collections.abc import Hashable, Sequence
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.config import settings
from app.embeddings.model import embed_query
from app.repositories import chunks as chunk_repo


@dataclass
class RetrievedChunk:
    id: uuid.UUID
    document_id: uuid.UUID
    filename: str
    page_number: int
    content: str
    score: float


def rrf_fuse(rankings: Sequence[Sequence[Hashable]], k: int = 60) -> list[tuple[Hashable, float]]:
    """Reciprocal Rank Fusion: score(d) = sum over lists of 1 / (k + rank)."""
    scores: dict[Hashable, float] = defaultdict(float)
    for ranking in rankings:
        for rank, item in enumerate(ranking, start=1):
            scores[item] += 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda kv: kv[1], reverse=True)


def retrieve(db: Session, project_id: uuid.UUID, query: str, top_k: int | None = None) -> list[RetrievedChunk]:
    """Hybrid retrieval, always scoped to project_id (never chosen by the LLM)."""
    top_k = top_k or settings.retrieval_top_k
    n = settings.retrieval_candidates
    sem = chunk_repo.semantic_ids(db, project_id, embed_query(query), n)
    kw = chunk_repo.keyword_ids(db, project_id, query, n)
    fused = rrf_fuse([sem, kw], k=settings.rrf_k)[:top_k]
    if not fused:
        return []
    rows = chunk_repo.get_many(db, project_id, [cid for cid, _ in fused])
    return [
        RetrievedChunk(r.id, r.document_id, r.filename, r.page_number, r.content, score)
        for cid, score in fused
        if (r := rows.get(cid)) is not None
    ]
