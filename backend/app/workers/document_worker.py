import logging
import uuid

from app.core.db import SessionLocal
from app.core.exceptions import IngestionError
from app.models import Document
from app.rag.ingestion import ingest_document

log = logging.getLogger(__name__)


def process_document(document_id: uuid.UUID) -> None:
    """Background entry point (FastAPI BackgroundTasks). Owns its own DB session and always sets a final status."""
    with SessionLocal() as db:
        doc = db.get(Document, document_id)
        if doc is None:
            return
        try:
            ingest_document(db, doc)
            doc.status, doc.error = "completed", None
        except IngestionError as e:
            db.rollback()
            doc.status, doc.error = "failed", str(e)
        except Exception:
            log.exception("Unexpected ingestion failure for %s", document_id)
            db.rollback()
            doc.status, doc.error = "failed", "Lỗi nội bộ khi xử lý tài liệu"
        db.commit()
