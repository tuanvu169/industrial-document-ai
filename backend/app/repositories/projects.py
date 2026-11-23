import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Project


def list_for_user(db: Session, user_id: uuid.UUID) -> list[Project]:
    return list(db.scalars(select(Project).where(Project.user_id == user_id).order_by(Project.created_at.desc())))


def get_owned(db: Session, project_id: uuid.UUID, user_id: uuid.UUID) -> Project | None:
    return db.scalar(select(Project).where(Project.id == project_id, Project.user_id == user_id))


def create(db: Session, user_id: uuid.UUID, name: str, description: str | None) -> Project:
    p = Project(user_id=user_id, name=name, description=description)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p
