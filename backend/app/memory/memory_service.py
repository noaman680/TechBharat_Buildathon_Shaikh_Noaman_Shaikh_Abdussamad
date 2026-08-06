"""Cross-meeting memory updates, run once a meeting completes. See docs/BLUEPRINT.md §7."""
from qdrant_client.models import PointStruct

from app.memory.qdrant_client import qdrant_client
from app.memory.neo4j_client import update_knowledge_graph
from app.services.embedding import embed


async def update_organizational_memory(meeting_id: str, state) -> None:
    # 1. Upsert meeting summary embedding in Qdrant
    await qdrant_client.upsert("meeting_summaries", [
        PointStruct(
            id=meeting_id,
            vector=await embed(state["meeting_report"]["executive_summary"]),
            payload={
                "org_id": state["organization_id"],
                "date": state["meeting_metadata"].get("date"),
                "title": state["meeting_metadata"].get("title"),
            },
        )
    ])

    # 2. Upsert action item embeddings for dedup lookups
    for item in state["approved_items"]:
        await qdrant_client.upsert("action_items", [
            PointStruct(
                id=item["id"],
                vector=await embed(item["title"] + " " + item["description"]),
                payload={**item, "meeting_id": meeting_id},
            )
        ])

    # 3. Update knowledge graph
    await update_knowledge_graph(meeting_id, state)
