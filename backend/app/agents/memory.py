"""Agent 9: Memory — enrich the current meeting with historical organizational context."""
from qdrant_client.models import Filter, FieldCondition, MatchValue

from app.agents.state import MeetingState
from app.db import db
from app.memory.qdrant_client import qdrant_client
from app.services.embedding import embed
from app.utils.memory import build_historical_context


async def memory_agent(state: MeetingState) -> MeetingState:
    """
    1. Semantic search over past meeting transcripts for related topics.
    2. Find carry-forward action items (incomplete from past meetings).
    3. Detect repeated commitments (same task promised before).
    4. Build context paragraph for the approval UI.
    5. Flag repeated delays as high priority.
    """
    query_embedding = await embed(state["meeting_report"]["executive_summary"])
    related = await qdrant_client.search(
        collection_name="meeting_summaries",
        query_vector=query_embedding,
        limit=5,
        query_filter=Filter(must=[
            FieldCondition(key="org_id", match=MatchValue(value=state["organization_id"]))
        ]),
    )

    owners = list({
        item["owner_email"] for item in state["resolved_items"] if item.get("owner_email")
    })
    overdue_items = await db.action_items.get_overdue_by_owners(owners)

    carry_forwards = []
    for item in state["resolved_items"]:
        similar = await qdrant_client.search(
            collection_name="action_items",
            query_vector=await embed(item["title"] + " " + item["description"]),
            limit=3,
            score_threshold=0.88,
        )
        if similar:
            item["is_repeat_commitment"] = True
            item["previous_commitment_ids"] = [s.id for s in similar]
            carry_forwards.append(item)

    historical_context = build_historical_context(related, overdue_items, carry_forwards)

    return {
        **state,
        "related_meeting_ids": [r.id for r in related],
        "historical_context": historical_context,
        "carry_forward_items": carry_forwards,
    }
