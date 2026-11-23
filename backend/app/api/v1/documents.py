import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, File, Response, UploadFile
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import CurrentUser, get_current_user
from app.repositories import documents as repo
from app.schemas import DocumentOut
from app.services import document_service
from app.services.project_service import get_owned_project
from app.workers.document_worker import process_document

router = APIRouter(prefix="/projects/{project_id}/documents", tags=["documents"])


@router.get("", response_model=list[DocumentOut])
def list_documents(project_id: uuid.UUID, db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    get_owned_project(db, user, project_id)
    return repo.list_by_project(db, project_id)


@router.post("", response_model=DocumentOut, status_code=202)
def upload_document(
    project_id: uuid.UUID,
    background: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    doc = document_service.create_from_upload(db, user, project_id, file)
    background.add_task(process_document, doc.id)
    return doc


@router.delete("/{document_id}", status_code=204)
def delete_document(project_id: uuid.UUID, document_id: uuid.UUID, db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    document_service.delete_document(db, user, project_id, document_id)
    return Response(status_code=204)
