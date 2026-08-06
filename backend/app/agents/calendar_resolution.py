"""Agent 8: Calendar Resolution — convert relative dates to exact ISO dates."""
import time
import json
import pytz
import dateparser
import structlog
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.agents.state import MeetingAgentState, AuditEntry
from app.config import settings
from app.prompts.calendar import CALENDAR_SYSTEM_PROMPT

logger = structlog.get_logger()


async def resolve_date_with_llm(raw: str, meeting_date: str, timezone: str, llm) -> dict:
    """Use LLM for complex date expressions dateparser cannot handle."""
    response = await llm.ainvoke([
        SystemMessage(content=CALENDAR_SYSTEM_PROMPT),
        HumanMessage(content=f"Date expression: \"{raw}\"\nMeeting date: {meeting_date}\nTimezone: {timezone}"),
    ])
    return json.loads(response.content)


async def calendar_resolution_node(state: MeetingAgentState) -> dict:
    """Resolve all relative date expressions to exact calendar dates."""
    start = time.perf_counter()
    items = state["verified_items"]
    meeting_date = datetime.fromisoformat(state.get("meeting_date", datetime.utcnow().isoformat()))
    timezone = state.get("timezone", "UTC")
    tz = pytz.timezone(timezone)

    llm = ChatOpenAI(model=settings.openai_fast_model, temperature=0,
                     response_format={"type": "json_object"})
    warnings = []

    for item in items:
        raw = (item.due_date_raw or "").strip()
        if not raw or raw.lower() in ("none", "tbd", "n/a", ""):
            continue

        # Try deterministic parsing first
        parsed = dateparser.parse(
            raw,
            settings={
                "RELATIVE_BASE": meeting_date,
                "TIMEZONE": timezone,
                "PREFER_DATES_FROM": "future",
                "RETURN_AS_TIMEZONE_AWARE": False,
            },
        )

        if parsed:
            item.due_date_resolved = parsed.date().isoformat()
        else:
            # Fall back to LLM
            try:
                result = await resolve_date_with_llm(raw, state["meeting_date"], timezone, llm)
                if result.get("needs_clarification"):
                    warnings.append(
                        f"Date \'{raw}\' for \'{item.title}\' needs clarification: "
                        f"{result.get('clarification_question', 'Please specify date')}"
                    )
                else:
                    item.due_date_resolved = result.get("resolved_date")
            except Exception as e:
                warnings.append(f"Could not resolve date \'{raw}\': {e}")

    duration_ms = int((time.perf_counter() - start) * 1000)
    resolved = sum(1 for i in items if i.due_date_resolved)
    audit = AuditEntry(
        timestamp=__import__("datetime").datetime.utcnow().isoformat(),
        agent="CalendarResolutionAgent",
        action="resolve_dates",
        output_summary=f"resolved={resolved}/{len(items)} dates",
        duration_ms=duration_ms,
    )

    return {
        "verified_items": items,
        "warnings": warnings,
        "current_phase": "dates_resolved",
        "audit_log": [audit],
    }
