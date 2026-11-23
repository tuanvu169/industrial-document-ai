import pytest

from app.processing.chunker import chunk_pages, chunk_text


def test_chunk_sizes_and_overlap():
    text = " ".join(f"w{i}" for i in range(25))
    chunks = chunk_text(text, size=10, overlap=3)
    assert chunks[0].split() == [f"w{i}" for i in range(10)]
    assert chunks[1].split()[:3] == ["w7", "w8", "w9"]  # overlap
    assert chunks[-1].split()[-1] == "w24"  # nothing lost


def test_short_text_single_chunk():
    assert chunk_text("hello world", size=500, overlap=80) == ["hello world"]


def test_empty_text():
    assert chunk_text("", size=10, overlap=2) == []


def test_invalid_params():
    with pytest.raises(ValueError):
        chunk_text("a b c", size=5, overlap=5)


def test_pages_keep_page_numbers():
    chunks = chunk_pages([(1, "a b c"), (3, "d e f")], size=10, overlap=2)
    assert [(c.index, c.page_number) for c in chunks] == [(0, 1), (1, 3)]
