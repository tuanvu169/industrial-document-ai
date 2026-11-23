import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.core.security import CurrentUser
from app.integrations import supabase as storage
from app.models import Project
from app.repositories import documents as doc_repo
from app.repositories import projects as project_repo


def get_owned_project(db: Session, user: CurrentUser, project_id: uuid.UUID) -> Project:
    """Single ownership gate. 404 (not 403) so project existence is not leaked."""
    project = project_repo.get_owned(db, project_id, user.id)
    if project is None:
        raise NotFoundError("Không tìm thấy project")
    return project


def delete_project(db: Session, user: CurrentUser, project_id: uuid.UUID) -> None:
    project = get_owned_project(db, user, project_id)
    paths = doc_repo.paths_for_project(db, project.id)
    db.delete(project)  # DB cascades documents, chunks, conversations, messages
    db.commit()
    try:
        storage.remove_files(paths)
    except Exception:  # best effort: DB is already consistent
        pass
