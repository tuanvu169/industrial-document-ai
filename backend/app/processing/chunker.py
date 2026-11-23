import re
from collections.abc import Callable
from dataclasses import dataclass

OffsetFn = Callable[[str], list[tuple[int, int]]]


def word_offsets(text: str) -> list[tuple[int, int]]:
    """Fallback tokenizer: 1 word = 1 token. Production passes the embedding model's tokenizer."""
    return [m.span() for m in re.finditer(r"\S+", text)]


@dataclass
class Chunk:
    index: int
    page_number: int
    content: str


def chunk_text(text: str, size: int, overlap: int, offsets_fn: OffsetFn = word_offsets) -> list[str]:
    """Sliding window over tokens; slices the original text by token character offsets."""
    if size <= 0 or not 0 <= overlap < size:
        raise ValueError("require size > 0 and 0 <= overlap < size")
    offs = offsets_fn(text)
    n = len(offs)
    out: list[str] = []
    start = 0
    while start < n:
        end = min(start + size, n)
        piece = text[offs[start][0] : offs[end - 1][1]].strip()
        if piece:
            out.append(piece)
        if end == n:
            break
        start = end - overlap
    return out


def chunk_pages(
    pages: list[tuple[int, str]], size: int, overlap: int, offsets_fn: OffsetFn = word_offsets
) -> list[Chunk]:
    """Chunk per page so every chunk keeps an exact page number for citations."""
    chunks: list[Chunk] = []
    for page_no, text in pages:
        for piece in chunk_text(text, size, overlap, offsets_fn):
            chunks.append(Chunk(index=len(chunks), page_number=page_no, content=piece))
    return chunks
