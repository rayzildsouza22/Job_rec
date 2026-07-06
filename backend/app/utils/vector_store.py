"""Qdrant vector-store wrapper.

- One collection: `jobs` (name configurable via QDRANT_JOBS_COLLECTION).
- Each point = job embedding + payload {"job_id": <int>}.
- PostgreSQL remains the source of truth; Qdrant only stores vectors + job_id.
"""

import os
from typing import List, Tuple

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from app.utils.embeddings import embed_text, embedding_dimension

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY") or None
COLLECTION = os.getenv("QDRANT_JOBS_COLLECTION", "jobs")

_client: QdrantClient | None = None


def get_client() -> QdrantClient:
    """Cached Qdrant client. Uses HTTP; supports Qdrant Cloud when API key set."""
    global _client
    if _client is None:
        _client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    return _client


def ensure_collection() -> None:
    """Create the jobs collection if it does not exist yet."""
    client = get_client()
    existing = {c.name for c in client.get_collections().collections}
    if COLLECTION not in existing:
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=qmodels.VectorParams(
                size=embedding_dimension(),
                distance=qmodels.Distance.COSINE,
            ),
        )


def upsert_job(job_id: int, text: str) -> None:
    """Embed the job's text and upsert it into Qdrant with payload job_id."""
    ensure_collection()
    vector = embed_text(text)
    get_client().upsert(
        collection_name=COLLECTION,
        points=[
            qmodels.PointStruct(
                id=job_id,
                vector=vector,
                payload={"job_id": job_id},
            )
        ],
    )


def delete_job(job_id: int) -> None:
    """Remove a job's vector from Qdrant."""
    try:
        get_client().delete(
            collection_name=COLLECTION,
            points_selector=qmodels.PointIdsList(points=[job_id]),
        )
    except Exception:
        # Ignore if collection doesn't exist yet.
        pass


def search(query_text: str, top_k: int = 5) -> List[Tuple[int, float]]:
    """Semantic search. Returns list of (job_id, similarity)."""
    ensure_collection()
    vector = embed_text(query_text)
    results = get_client().search(
        collection_name=COLLECTION,
        query_vector=vector,
        limit=top_k,
    )
    output: List[Tuple[int, float]] = []
    for point in results:
        payload = point.payload or {}
        job_id = payload.get("job_id", point.id)
        output.append((int(job_id), float(point.score)))
    return output
