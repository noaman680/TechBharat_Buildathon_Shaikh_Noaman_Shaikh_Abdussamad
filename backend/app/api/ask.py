"""
GET /api/meetings/search?q=...        -> Semantic search over past meetings
GET /api/ask?q=...&org_id=...         -> RAG Q&A over org meeting history
GET /api/owners/{email}/items         -> All tasks assigned to a person
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/meetings/search")
async def search_meetings(q: str):
    raise NotImplementedError("TODO: embed(q) + qdrant search over meeting_summaries")


@router.get("/ask")
async def ask(q: str, org_id: str):
    """Cross-meeting Q&A — see answer_meeting_question() in docs/BLUEPRINT.md §9."""
    raise NotImplementedError("TODO: retrieve chunks + decisions, answer with citations")


@router.get("/owners/{email}/items")
async def owner_items(email: str):
    raise NotImplementedError("TODO: fetch action_items for owner_email")
