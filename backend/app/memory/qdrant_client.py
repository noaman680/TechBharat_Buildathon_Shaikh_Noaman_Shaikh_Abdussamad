"""Qdrant vector database client."""
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.config import settings
import uuid

COLLECTION = settings.qdrant_collection
VECTOR_DIM = 1536  # text-embedding-3-small


async def get_qdrant() -> AsyncQdrantClient:
    return AsyncQdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key or None)


async def ensure_collection():
    client = await get_qdrant()
    collections = [c.name for c in (await client.get_collections()).collections]
    if COLLECTION not in collections:
        await client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=VECTOR_DIM, distance=Distance.COSINE),
        )


async def upsert_vectors(points: list[dict]):
    client = await get_qdrant()
    structs = [
        PointStruct(
            id=p.get("id", str(uuid.uuid4())),
            vector=p["vector"],
            payload=p.get("metadata", {}),
        )
        for p in points
    ]
    await client.upsert(collection_name=COLLECTION, points=structs)


async def search_similar(vector: list[float], filter_dict: dict = None, top_k: int = 5) -> list[dict]:
    from qdrant_client.models import Filter, FieldCondition, MatchValue
    client = await get_qdrant()

    query_filter = None
    if filter_dict:
        conditions = [FieldCondition(key=k, match=MatchValue(value=v)) for k, v in filter_dict.items()]
        query_filter = Filter(must=conditions)

    results = await client.search(
        collection_name=COLLECTION,
        query_vector=vector,
        query_filter=query_filter,
        limit=top_k,
        with_payload=True,
    )
    return [{"id": r.id, "score": r.score, "metadata": r.payload} for r in results]
