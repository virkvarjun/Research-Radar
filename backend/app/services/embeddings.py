"""Pluggable embedding provider. Default: OpenAI text-embedding-3-small."""

import logging
from typing import Optional

import numpy as np

from app.config import settings

logger = logging.getLogger(__name__)

_client = None


def _get_openai_client():
    global _client
    if _client is None:
        from openai import OpenAI
        _client = OpenAI(api_key=settings.openai_api_key)
    return _client


async def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts. Returns list of embedding vectors."""
    if not texts:
        return []

    if settings.embedding_provider == "openai":
        return _embed_openai(texts)
    else:
        raise ValueError(f"Unknown embedding provider: {settings.embedding_provider}")


def _embed_openai(texts: list[str]) -> list[list[float]]:
    client = _get_openai_client()
    # OpenAI batch limit is 2048, chunk if needed
    all_embeddings = []
    batch_size = 512
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        response = client.embeddings.create(
            model=settings.embedding_model,
            input=batch,
        )
        all_embeddings.extend([item.embedding for item in response.data])
    return all_embeddings


async def embed_text(text: str) -> Optional[list[float]]:
    """Embed a single text string."""
    if not text or not text.strip():
        return None
    results = await embed_texts([text])
    return results[0] if results else None


def paper_text_for_embedding(title: str, abstract: Optional[str] = None) -> str:
    """Combine title + abstract for paper embedding."""
    parts = [title]
    if abstract:
        parts.append(abstract)
    return " ".join(parts)


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    a_arr = np.array(a, dtype=np.float64)
    b_arr = np.array(b, dtype=np.float64)
    norm_a = np.linalg.norm(a_arr)
    norm_b = np.linalg.norm(b_arr)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a_arr, b_arr) / (norm_a * norm_b))


def normalize_vector(v: list[float]) -> list[float]:
    """L2-normalize a vector."""
    arr = np.array(v, dtype=np.float64)
    norm = np.linalg.norm(arr)
    if norm == 0:
        return v
    return (arr / norm).tolist()
