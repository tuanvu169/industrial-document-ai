import re

from app.inference.gemini_inference import generate
from app.prompts.rag import CONDENSE_SYSTEM, SYSTEM_PROMPT, build_user_prompt
from app.rag.retriever import RetrievedChunk
from app.schemas import Source

_CITE = re.compile(r"\[([\d,\s]+)\]")


def condense_question(question: str, history: list[tuple[str, str]]) -> str:
    """Turn a follow-up ("còn trang nào nữa?") into a standalone retrieval query."""
    turns = history + [("user", question)]
    return generate(CONDENSE_SYSTEM, turns, temperature=0.0) or question


def build_context_blocks(chunks: list[RetrievedChunk]) -> list[str]:
    return [f"[{i}] (Tài liệu: {c.filename}, trang {c.page_number})\n{c.content}" for i, c in enumerate(chunks, 1)]


def cited_indices(answer: str, max_index: int) -> list[int]:
    found: list[int] = []
    for group in _CITE.findall(answer):
        for tok in group.split(","):
            if tok.strip().isdigit() and 1 <= int(tok) <= max_index and int(tok) not in found:
                found.append(int(tok))
    return sorted(found)


def answer_from_context(question: str, chunks: list[RetrievedChunk], history: list[tuple[str, str]]) -> tuple[str, list[Source]]:
    prompt = build_user_prompt(question, build_context_blocks(chunks))
    text = generate(SYSTEM_PROMPT, history + [("user", prompt)])
    used = cited_indices(text, len(chunks))
    sources = [
        Source(
            index=i,
            document_id=chunks[i - 1].document_id,
            filename=chunks[i - 1].filename,
            page_number=chunks[i - 1].page_number,
            snippet=chunks[i - 1].content[:300],
        )
        for i in used
    ]
    return text, sources
