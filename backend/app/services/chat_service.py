import uuid

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import NotFoundError
from app.core.security import CurrentUser
from app.models import Conversation, Message
from app.rag import pipeline
from app.repositories import conversations as conv_repo
from app.services.project_service import get_owned_project


def get_owned_conversation(db: Session, user: CurrentUser, project_id: uuid.UUID, conversation_id: uuid.UUID) -> Conversation:
    project = get_owned_project(db, user, project_id)
    conv = conv_repo.get_owned(db, conversation_id, project.id, user.id)
    if conv is None:
        raise NotFoundError("Không tìm thấy cuộc hội thoại")
    return conv


def chat(db: Session, user: CurrentUser, project_id: uuid.UUID, conversation_id: uuid.UUID | None, text: str) -> tuple[Conversation, Message]:
    project = get_owned_project(db, user, project_id)
    if conversation_id:
        conv = get_owned_conversation(db, user, project.id, conversation_id)
        past = conv_repo.recent_messages(db, conv.id, settings.history_messages)
        history = [("user" if m.role == "user" else "model", m.content) for m in past]
    else:
        conv = conv_repo.create(db, project.id, user.id, title=text.strip()[:60])
        history = []

    conv_repo.add_message(db, conv.id, "user", text)
    result = pipeline.run(db, project.id, text, history)  # may raise UpstreamError; user message is kept
    reply = conv_repo.add_message(
        db, conv.id, "assistant", result.answer, [s.model_dump(mode="json") for s in result.sources]
    )
    return conv, reply
