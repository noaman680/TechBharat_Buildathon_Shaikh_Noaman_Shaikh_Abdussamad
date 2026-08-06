"""Agent 8: Calendar Resolution — convert natural-language dates into exact ISO dates."""
import json

from app.agents.state import MeetingState
from app.clients.claude import claude_haiku_client
from app.prompts.calendar import CALENDAR_PROMPT


async def calendar_resolution_agent(state: MeetingState) -> MeetingState:
    final_items = []
    tz = state["meeting_metadata"].get("timezone", "UTC")
    meeting_date = state["meeting_metadata"]["date"]

    for item in state["resolved_items"]:
        response = await claude_haiku_client.messages.create(
            model="claude-haiku-4-5-20251001",
            messages=[{"role": "user", "content": CALENDAR_PROMPT.format(
                meeting_date=meeting_date,
                timezone=tz,
                calendar_context=state["meeting_metadata"].get("sprint_context", ""),
                date_raw=item["due_date_raw"],
            )}],
            max_tokens=200,
        )
        resolution = json.loads(response.content[0].text)
        item["due_date_resolved"] = resolution["resolved_date"]
        item["due_date_confidence"] = resolution["confidence"]
        final_items.append(item)

    return {**state, "resolved_items": final_items}
