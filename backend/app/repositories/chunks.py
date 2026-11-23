import re
import uuid

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models import Document, DocumentChunk
from app.processing.chunker import Chunk


def replace_for_document(db: Session, doc: Document, chunks: list[Chunk], vectors: list[list[float]]) -> None:
    db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == doc.id))
    db.add_all(
        DocumentChunk(
            project_id=doc.project_id,
            document_id=doc.id,
            chunk_index=c.index,
            filename=doc.filename,
            page_number=c.page_number,
            content=c.content,
            embedding=v,
        )
        for c, v in zip(chunks, vectors, strict=True)
    )
    db.flush()


def semantic_ids(db: Session, project_id: uuid.UUID, qvec: list[float], limit: int) -> list[uuid.UUID]:
    stmt = (
        select(DocumentChunk.id)
        .where(DocumentChunk.project_id == project_id)  # mandatory project isolation
        .order_by(DocumentChunk.embedding.cosine_distance(qvec))
        .limit(limit)
    )
    return list(db.scalars(stmt))


def keyword_expression(query: str, max_terms: int = 20) -> str | None:
    """OR-query of sanitized terms (natural-language questions rarely match with AND)."""
    terms = [t.lower() for t in re.findall(r"[^\W_]+", query) if len(t) > 1]
    terms = list(dict.fromkeys(terms))[:max_terms]
    return " | ".join(terms) if terms else None


def keyword_ids(db: Session, project_id: uuid.UUID, query: str, limit: int) -> list[uuid.UUID]:
    expr = keyword_expression(query)
    if not expr:
        return []
    tsq = func.to_tsquery("simple", expr)
    stmt = (
        select(DocumentChunk.id)
        .where(DocumentChunk.project_id == project_id, DocumentChunk.fts.op("@@")(tsq))
        .order_by(func.ts_rank_cd(DocumentChunk.fts, tsq).desc())
        .limit(limit)
    )
    return list(db.scalars(stmt))


def get_many(db: Session, project_id: uuid.UUID, ids: list[uuid.UUID]) -> dict[uuid.UUID, DocumentChunk]:
    rows = db.scalars(select(DocumentChunk).where(DocumentChunk.project_id == project_id, DocumentChunk.id.in_(ids)))
    return {r.id: r for r in rows}
