"""Agent 4: Planning — analyze meeting type and plan extraction strategy."""
import time
import json
import structlog
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.agents.state import MeetingAgentState, AuditEntry
from app.config import settings
from app.prompts.planning import PLANNING_SYSTEM_PROMPT

logger = structlog.get_logger()


async def planning_node(state: MeetingAgentState) -> dict:
    """Analyze meeting and create extraction plan."""
    start = time.perf_counter()
    transcript = state.get("transcript_raw", "")[:6000]

    llm = ChatOpenAI(model=settings.openai_fast_model, temperature=0)

    try:
        response = await llm.ainvoke([
            SystemMessage(content=PLANNING_SYSTEM_PROMPT),
            HumanMessage(content=f"Meeting Date: {state['meeting_date']}\nTimezone: {state['timezone']}\n\nTranscript (first 6000 chars):\n{transcript}"),
        ])
        plan = json.loads(response.content)
    except Exception as e:
        logger.warning("Planning LLM failed, using defaults", error=str(e))
        plan = {
            "meeting_type": "general",
            "participant_count": len(state.get("speakers", [])),
            "complexity": "medium",
            "extraction_steps": ["decisions", "action_items", "risks", "questions"],
        }

    duration_ms = int((time.perf_counter() - start) * 1000)
    audit = AuditEntry(
        timestamp=__import__("datetime").datetime.utcnow().isoformat(),
        agent="PlanningAgent",
        action="analyze_and_plan",
        output_summary=f"type={plan.get('meeting_type')}, steps={len(plan.get('extraction_steps', []))}",
        duration_ms=duration_ms,
    )

    return {
        "planning_steps": plan.get("extraction_steps", []),
        "current_phase": "planned",
        "audit_log": [audit],
    }
