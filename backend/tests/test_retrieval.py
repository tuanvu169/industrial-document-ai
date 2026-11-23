from app.evaluation.metrics import citation_accuracy, recall_at_k, reciprocal_rank
from app.rag.generator import cited_indices
from app.rag.retriever import rrf_fuse
from app.repositories.chunks import keyword_expression


def test_rrf_prefers_items_in_both_lists():
    fused = rrf_fuse([["a", "b", "c"], ["c", "d", "a"]], k=60)
    ids = [i for i, _ in fused]
    assert ids[0] == "a"  # tie with "c" (1/61 + 1/63 each); insertion order wins
    assert set(ids[:2]) == {"a", "c"}
    assert set(ids) == {"a", "b", "c", "d"}


def test_rrf_empty():
    assert rrf_fuse([[], []]) == []


def test_keyword_expression_sanitizes():
    assert keyword_expression("Áp suất van & 'DROP TABLE'; a") == "áp | suất | van | drop | table"
    assert keyword_expression("?! _") is None


def test_cited_indices():
    assert cited_indices("Van A [1][3]. Xem thêm [2, 3] và [9].", 4) == [1, 2, 3]
    assert cited_indices("không có nguồn", 4) == []


def test_metrics():
    rel = {("a.pdf", 1), ("b.pdf", 2)}
    got = [("x.pdf", 9), ("a.pdf", 1), ("b.pdf", 2)]
    assert recall_at_k(got, rel, 2) == 0.5
    assert reciprocal_rank(got, rel) == 0.5
    assert citation_accuracy([("a.pdf", 1), ("z.pdf", 1)], rel) == 0.5
