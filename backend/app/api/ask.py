"""RAG Q&A — ask questions about your meetings."""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class AskRequest(BaseModel):
    org_id: str
    question: str
    meeting_ids: list[str] = []


@router.post("")
async def ask_about_meetings(body: AskRequest):
    """Answer questions about meetings using RAG over stored embeddings."""
    from app.memory.memory_service import MemoryService
    from langchain_openai import ChatOpenAI
    from app.config import settings

    memory = MemoryService()
    related = await memory.find_related_meetings(body.question, body.org_id)

    # Build context from related meetings
    context = f"Question: {body.question}\nRelated meeting IDs: {related}\n"

    llm = ChatOpenAI(model=settings.openai_model, temperature=0)
    response = await llm.ainvoke([
        {"role": "system", "content": "You are a meeting intelligence assistant. Answer questions about past meetings based on the provided context."},
        {"role": "user", "content": context},
    ])

    return {
        "answer": response.content,
        "sources": related,
        "question": body.question,
    }
