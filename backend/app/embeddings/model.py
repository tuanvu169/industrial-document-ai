from functools import lru_cache

from app.core.config import settings


@lru_cache
def get_model():
    from sentence_transformers import SentenceTransformer  # lazy: heavy import

    return SentenceTransformer(settings.embedding_model)


def tokenizer_offsets(text: str) -> list[tuple[int, int]]:
    tok = get_model().tokenizer
    enc = tok(text, add_special_tokens=False, return_offsets_mapping=True, truncation=False, verbose=False)
    return [tuple(o) for o in enc["offset_mapping"]]


def embed_passages(texts: list[str], batch_size: int = 32) -> list[list[float]]:
    # e5 models require the "passage: " / "query: " prefixes
    vecs = get_model().encode([f"passage: {t}" for t in texts], batch_size=batch_size, normalize_embeddings=True)
    return vecs.tolist()


def embed_query(query: str) -> list[float]:
    return get_model().encode(f"query: {query}", normalize_embeddings=True).tolist()
