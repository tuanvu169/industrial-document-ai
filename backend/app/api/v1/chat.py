import uuid

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import CurrentUser, get_current_user
from app.repositories import conversations as repo
from app.schemas import ChatRequest, ChatResponse, ConversationOut, MessageOut
from app.services import chat_service
from app.services.project_service import get_owned_project

router = APIRouter(prefix="/projects/{project_id}", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(project_id: uuid.UUID, body: ChatRequest, db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    conv, reply = chat_service.chat(db, user, project_id, body.conversation_id, body.message.strip())
    return ChatResponse(conversation_id=conv.id, message=MessageOut.model_validate(reply))


@router.get("/conversations", response_model=list[ConversationOut])
def list_conversations(project_id: uuid.UUID, db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    get_owned_project(db, user, project_id)
    return repo.list_for_project(db, project_id, user.id)


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageOut])
def list_messages(project_id: uuid.UUID, conversation_id: uuid.UUID, db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    conv = chat_service.get_owned_conversation(db, user, project_id, conversation_id)
    return repo.messages(db, conv.id)


@router.delete("/conversations/{conversation_id}", status_code=204)
def delete_conversation(project_id: uuid.UUID, conversation_id: uuid.UUID, db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    conv = chat_service.get_owned_conversation(db, user, project_id, conversation_id)
    db.delete(conv)
    db.commit()
    return Response(status_code=204)
