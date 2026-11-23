import os
import uuid

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import NotFoundError, PayloadTooLarge, UpstreamError, ValidationFailed
from app.core.security import CurrentUser
from app.integrations import supabase as storage
from app.models import Document
from app.repositories import documents as doc_repo
from app.services.project_service import get_owned_project


def create_from_upload(db: Session, user: CurrentUser, project_id: uuid.UUID, file: UploadFile) -> Document:
    project = get_owned_project(db, user, project_id)
    filename = os.path.basename(file.filename or "document.pdf")[:200]
    if not filename.lower().endswith(".pdf"):
        raise ValidationFailed("Chỉ hỗ trợ file PDF")

    limit = settings.max_upload_mb * 1024 * 1024
    data = file.file.read(limit + 1)
    if len(data) > limit:
        raise PayloadTooLarge(f"File vượt quá {settings.max_upload_mb} MB")
    if not data.startswith(b"%PDF"):
        raise ValidationFailed("File không phải PDF hợp lệ")

    doc_id = uuid.uuid4()
    path = f"{user.id}/{project.id}/{doc_id}.pdf"
    try:
        storage.upload_file(path, data)
    except Exception as e:
        raise UpstreamError(f"Không lưu được file lên Supabase Storage: {e}")

    doc = Document(id=doc_id, project_id=project.id, filename=filename, storage_path=path, status="processing")
    try:
        db.add(doc)
        db.commit()
        db.refresh(doc)
    except Exception:
        db.rollback()
        storage.remove_files([path])
        raise
    return doc


def delete_document(db: Session, user: CurrentUser, project_id: uuid.UUID, document_id: uuid.UUID) -> None:
    project = get_owned_project(db, user, project_id)
    doc = doc_repo.get(db, document_id, project.id)
    if doc is None:
        raise NotFoundError("Không tìm thấy tài liệu")
    path = doc.storage_path
    db.delete(doc)  # chunks cascade
    db.commit()
    try:
        storage.remove_files([path])
    except Exception:
        pass
