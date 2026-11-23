from dataclasses import dataclass

import pymupdf  # PyMuPDF

from app.core.config import settings
from app.core.exceptions import IngestionError


@dataclass
class ParsedDocument:
    page_count: int
    pages: list[tuple[int, str]]  # (1-based page number, raw text)


def parse_pdf(data: bytes) -> ParsedDocument:
    try:
        doc = pymupdf.open(stream=data, filetype="pdf")
    except Exception as e:
        raise IngestionError(f"Không đọc được file PDF: {e}")
    with doc:
        if doc.needs_pass:
            raise IngestionError("PDF được bảo vệ bằng mật khẩu")
        if doc.page_count > settings.max_pages:
            raise IngestionError(f"PDF vượt quá {settings.max_pages} trang")
        pages = [(i + 1, page.get_text("text")) for i, page in enumerate(doc)]
        return ParsedDocument(page_count=doc.page_count, pages=pages)
