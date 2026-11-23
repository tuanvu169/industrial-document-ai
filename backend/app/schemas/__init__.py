import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)


class ProjectOut(ORM):
    id: uuid.UUID
    name: str
    description: str | None
    created_at: datetime


class DocumentOut(ORM):
    id: uuid.UUID
    project_id: uuid.UUID
    filename: str
    status: str
    error: str | None
    page_count: int | None
    created_at: datetime


class ConversationOut(ORM):
    id: uuid.UUID
    project_id: uuid.UUID
    title: str
    created_at: datetime


class Source(BaseModel):
    index: int
    document_id: uuid.UUID
    filename: str
    page_number: int
    snippet: str


class MessageOut(ORM):
    id: uuid.UUID
    role: str
    content: str
    sources: list[Source]
    created_at: datetime


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: uuid.UUID | None = None


class ChatResponse(BaseModel):
    conversation_id: uuid.UUID
    message: MessageOut
