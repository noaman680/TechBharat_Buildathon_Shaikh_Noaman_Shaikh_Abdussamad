"""High-level memory service combining Qdrant + Neo4j."""
import structlog
from app.memory.qdrant_client import upsert_vectors, search_similar, ensure_collection
from app.memory.neo4j_client import (
    create_meeting_node, create_task_node, get_overdue_tasks as _get_overdue
)

logger = structlog.get_logger()
DUPLICATE_THRESHOLD = 0.92


class MemoryService:
    async def embed(self, text: str) -> list[float]:
        try:
            from openai import AsyncOpenAI
            from app.config import settings
            client = AsyncOpenAI(api_key=settings.openai_api_key)
            resp = await client.embeddings.create(model="text-embedding-3-small", input=text)
            return resp.data[0].embedding
        except Exception as e:
            logger.warning("Embedding failed", error=str(e))
            return [0.0] * 1536

    async def is_duplicate(self, text: str, org_id: str) -> tuple[bool, str | None]:
        try:
            await ensure_collection()
            vector = await self.embed(text)
            results = await search_similar(
                vector=vector,
                filter_dict={"org_id": org_id, "type": "action_item"},
                top_k=3,
            )
            for r in results:
                if r["score"] > DUPLICATE_THRESHOLD:
                    return True, r["metadata"].get("title")
        except Exception as e:
            logger.warning("Duplicate check failed", error=str(e))
        return False, None

    async def store_meeting_embedding(self, meeting_id: str, org_id: str,
                                       summary: str, items: list):
        try:
            await ensure_collection()
            vector = await self.embed(summary)
            await upsert_vectors([{
                "id": meeting_id,
                "vector": vector,
                "metadata": {"org_id": org_id, "type": "meeting", "summary": summary[:500]},
            }])
            for item in items:
                item_vector = await self.embed(f"{item.title} {item.description}")
                await upsert_vectors([{
                    "id": item.id,
                    "vector": item_vector,
                    "metadata": {
                        "org_id": org_id, "type": "action_item",
                        "title": item.title, "meeting_id": meeting_id,
                    },
                }])
        except Exception as e:
            logger.warning("Store embedding failed", error=str(e))

    async def find_related_meetings(self, summary: str, org_id: str) -> list[str]:
        try:
            vector = await self.embed(summary)
            results = await search_similar(
                vector=vector,
                filter_dict={"org_id": org_id, "type": "meeting"},
                top_k=3,
            )
            return [r["id"] for r in results if r["score"] > 0.7]
        except Exception as e:
            logger.warning("Related meetings search failed", error=str(e))
            return []

    async def get_overdue_tasks(self, org_id: str, owner_emails: list[str]) -> list[dict]:
        try:
            return await _get_overdue(org_id, owner_emails)
        except Exception as e:
            logger.warning("Overdue tasks query failed", error=str(e))
            return []

    async def get_recurring_owners(self, org_id: str) -> dict:
        return {}  # Extended in production from historical data
