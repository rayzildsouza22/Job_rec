"""Sentence-Transformer embeddings.

- Loads the model lazily (first call downloads/loads it once).
- Same model is used for jobs and for resume/query text so vectors are comparable.
- Default: sentence-transformers/all-MiniLM-L6-v2 (384-dim, fast, small).
"""

import os
from typing import List

from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
)

_model = None  # lazy singleton


def _get_model():
    global _model
    if _model is None:
        # Imported lazily so `import app` stays fast in tests / migrations.
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_text(text: str) -> List[float]:
    """Return a single embedding vector for a string."""
    model = _get_model()
    vector = model.encode(text, normalize_embeddings=True)
    return vector.tolist()


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Batch version, faster when embedding many jobs."""
    model = _get_model()
    vectors = model.encode(texts, normalize_embeddings=True)
    return [v.tolist() for v in vectors]


def embedding_dimension() -> int:
    """Return the vector dimension (needed when creating Qdrant collection)."""
    return _get_model().get_sentence_embedding_dimension()
