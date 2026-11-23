import logging

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import IngestionError
from app.embeddings.model import embed_passages, tokenizer_offsets
from app.integrations import supabase as storage
from app.models import Document
from app.processing.chunker import chunk_pages
from app.processing.cleaner import clean_text
from app.processing.parser import parse_pdf
from app.repositories import chunks as chunk_repo

log = logging.getLogger(__name__)


def ingest_document(db: Session, doc: Document) -> None:
    """download -> parse -> clean -> chunk -> embed -> store. Raises IngestionError on bad input."""
    parsed = parse_pdf(storage.download_file(doc.storage_path))
    pages = [(n, clean_text(t)) for n, t in parsed.pages]
    pages = [(n, t) for n, t in pages if t]
    if not pages:
        raise IngestionError("Không trích xuất được văn bản (PDF scan/ảnh? OCR chưa bật trong MVP)")
    chunks = chunk_pages(pages, settings.chunk_size_tokens, settings.chunk_overlap_tokens, tokenizer_offsets)
    vectors = embed_passages([c.content for c in chunks])
    chunk_repo.replace_for_document(db, doc, chunks, vectors)
    doc.page_count = parsed.page_count
    log.info("Indexed %s: %d pages, %d chunks", doc.filename, parsed.page_count, len(chunks))
