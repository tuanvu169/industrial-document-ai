def recall_at_k(retrieved: list[tuple[str, int]], relevant: set[tuple[str, int]], k: int) -> float:
    """Fraction of relevant (filename, page) pairs found in the top-k."""
    if not relevant:
        return 0.0
    return len(set(retrieved[:k]) & relevant) / len(relevant)


def reciprocal_rank(retrieved: list[tuple[str, int]], relevant: set[tuple[str, int]]) -> float:
    for rank, item in enumerate(retrieved, start=1):
        if item in relevant:
            return 1.0 / rank
    return 0.0


def citation_accuracy(cited: list[tuple[str, int]], relevant: set[tuple[str, int]]) -> float:
    """Share of cited (filename, page) pairs that are actually relevant."""
    if not cited:
        return 0.0
    return sum(1 for c in cited if c in relevant) / len(cited)
