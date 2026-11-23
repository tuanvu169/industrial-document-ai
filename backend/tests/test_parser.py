import pymupdf
import pytest

from app.core.exceptions import IngestionError
from app.processing.parser import parse_pdf


def _pdf(pages: list[str]) -> bytes:
    doc = pymupdf.open()
    for text in pages:
        doc.new_page().insert_text((72, 72), text)
    return doc.tobytes()


def test_parse_pdf_returns_page_numbers():
    parsed = parse_pdf(_pdf(["Pump pressure 5 bar", "Valve torque 40 Nm"]))
    assert parsed.page_count == 2
    assert [n for n, _ in parsed.pages] == [1, 2]
    assert "Valve torque" in parsed.pages[1][1]


def test_parse_rejects_garbage():
    with pytest.raises(IngestionError):
        parse_pdf(b"not a pdf")
