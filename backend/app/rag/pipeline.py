import uuid
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.rag import generator, retriever
from app.schemas import Source

NO_CONTEXT_ANSWER = (
    "Tôi chưa tìm thấy nội dung liên quan trong tài liệu của dự án này. "
    "Hãy kiểm tra rằng tài liệu đã được xử lý xong (trạng thái “Hoàn tất”) hoặc thử diễn đạt lại câu hỏi."
)


@dataclass
class RagResult:
    answer: str
    sources: list[Source] = field(default_factory=list)
    retrieved: list[retriever.RetrievedChunk] = field(default_factory=list)


def run(db: Session, project_id: uuid.UUID, question: str, history: list[tuple[str, str]]) -> RagResult:
    query = generator.condense_question(question, history) if history else question
    chunks = retriever.retrieve(db, project_id, query)
    if not chunks:
        return RagResult(answer=NO_CONTEXT_ANSWER)
    text, sources = generator.answer_from_context(question, chunks, history)
    return RagResult(answer=text, sources=sources, retrieved=chunks)
