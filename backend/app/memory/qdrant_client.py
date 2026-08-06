"""Qdrant client + collection definitions. See docs/BLUEPRINT.md §9."""
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance

from app.config import settings

qdrant_client = AsyncQdrantClient(url=settings.QDRANT_URL)

COLLECTIONS = {
    "meeting_summaries": {
        "vector_size": 3072,
        "distance": Distance.COSINE,
        "purpose": "Find related past meetings for context enrichment",
    },
    "action_items": {
        "vector_size": 3072,
        "distance": Distance.COSINE,
        "purpose": "Semantic dedup of new items vs historical tasks",
    },
    "transcript_chunks": {
        "vector_size": 3072,
        "distance": Distance.COSINE,
        "purpose": "RAG over meeting transcripts for Q&A queries",
    },
    "decisions": {
        "vector_size": 3072,
        "distance": Distance.COSINE,
        "purpose": "Find prior decisions relevant to current discussion",
    },
}
