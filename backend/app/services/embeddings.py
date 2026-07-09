from functools import lru_cache

from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2


@lru_cache(maxsize=1)
def get_embedding_fn() -> ONNXMiniLM_L6_V2:
    return ONNXMiniLM_L6_V2()


def embed_texts(texts: list[str]) -> list[list[float]]:
    return get_embedding_fn()(texts)
