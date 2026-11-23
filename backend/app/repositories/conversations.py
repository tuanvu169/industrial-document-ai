import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Conversation, Message


def list_for_project(db: Session, project_id: uuid.UUID, user_id: uuid.UUID) -> list[Conversation]:
    stmt = (
        select(Conversation)
        .where(Conversation.project_id == project_id, Conversation.user_id == user_id)
        .order_by(Conversation.created_at.desc())
    )
    return list(db.scalars(stmt))


def get_owned(db: Session, conversation_id: uuid.UUID, project_id: uuid.UUID, user_id: uuid.UUID) -> Conversation | None:
    return db.scalar(
        select(Conversation).where(
            Conversation.id == conversation_id, Conversation.project_id == project_id, Conversation.user_id == user_id
        )
    )


def create(db: Session, project_id: uuid.UUID, user_id: uuid.UUID, title: str) -> Conversation:
    c = Conversation(project_id=project_id, user_id=user_id, title=title)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def messages(db: Session, conversation_id: uuid.UUID) -> list[Message]:
    return list(db.scalars(select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at)))


def recent_messages(db: Session, conversation_id: uuid.UUID, limit: int) -> list[Message]:
    rows = db.scalars(
        select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at.desc()).limit(limit)
    )
    return list(reversed(list(rows)))


def add_message(db: Session, conversation_id: uuid.UUID, role: str, content: str, sources: list | None = None) -> Message:
    m = Message(conversation_id=conversation_id, role=role, content=content, sources=sources or [])
    db.add(m)
    db.commit()
    db.refresh(m)
    return m
