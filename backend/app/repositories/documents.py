import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Document


def list_by_project(db: Session, project_id: uuid.UUID) -> list[Document]:
    return list(db.scalars(select(Document).where(Document.project_id == project_id).order_by(Document.created_at.desc())))


def get(db: Session, document_id: uuid.UUID, project_id: uuid.UUID) -> Document | None:
    return db.scalar(select(Document).where(Document.id == document_id, Document.project_id == project_id))


def paths_for_project(db: Session, project_id: uuid.UUID) -> list[str]:
    return list(db.scalars(select(Document.storage_path).where(Document.project_id == project_id)))
